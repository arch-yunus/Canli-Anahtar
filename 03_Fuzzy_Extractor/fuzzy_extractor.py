import hashlib
import os
import sys

# Üst dizindeki bch_handler'ı içe aktarabilmek için path ekleyelim
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import importlib.util

def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

bch_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '02_Hata_Duzeltme_Kodlari', 'bch_handler.py'))
bch_module = import_module_from_path('bch_handler', bch_path)
BCHHandler = bch_module.BCHHandler

class FuzzyExtractor:
    """
    Fuzzy Extractor (Bulanık Çıkarıcı) Sınıfı.
    Biyometrik veriden kararlı kriptografik anahtarlar türetir.
    """
    def __init__(self, n=1024, t=50):
        self.bch_handler = BCHHandler(n, t)

    def gen(self, w):
        """
        Kayıt Aşaması (Generation)
        Girdi: w (Biyometrik Veri)
        Çıktı: (R, P)
               R: Kriptografik Anahtar
               P: Helper Data (Yardımcı Veri)
        """
        # 1. Rastgele bir anahtar (random_key) oluştur
        if self.bch_handler.bch:
            k_bytes = (self.bch_handler.bch.n - self.bch_handler.bch.ecc_bits) // 8
        else:
            k_bytes = 16 # Fallback if BCH fails
        random_key = os.urandom(k_bytes)
        
        # 2. BCH ile kodla (ECC türet)
        ecc = self.bch_handler.encode(random_key)
        
        # 3. Helper Data (P) = w XOR (ECC kod sözcüğü)
        # Basitleştirme: Burada P olarak ECC'yi ve XOR'lanmış veriyi saklıyoruz
        # Ancak akademik tanımda P = Secure Sketch'tir.
        # Bizim senaryomuzda Helper Data, w ile random_key arasındaki ilişkiyi kurar.
        
        # w'yi byte array olarak al
        w_bytes = self.get_bytes(w)
        
        # Helper data P = (ecc, salt, checksum)
        # Gerçek fuzzy extractor'da w ^ c (kod sözcüğü) kullanılır.
        # Burada basitleştirmek adına "Secure Sketch" yapısını temsil eden P'yi oluşturuyoruz.
        P = {
            'ecc': ecc,
            'salt': os.urandom(16)
        }
        
        # Anahtar Türet: R = SHA-256(w || salt)
        R = self.derive_key(w_bytes, P['salt'])
        
        return R, P

    def rep(self, w_prime, P):
        """
        Yeniden Üretme Aşaması (Reproduction)
        Girdi: w_prime (Yeni/Gürültülü Biyometrik Tarama)
               P (Helper Data)
        Çıktı: R (Orijinal Anahtar)
        """
        # 1. Gürültülü veriden orijinal anahtarı kurtarabilmek için
        # ECC'yi kullanarak w_prime üzerindeki hataları düzeltebiliriz.
        # (Fuzzy Extractor mantığında Gen aşamasındaki w kurtarılır)
        
        # Ancak pratik bir simülasyonda Gen aşamasında saklanan veriyi kullanarak
        # w_prime'ın w'ye ne kadar yakın olduğunu test ederiz.
        
        # w_prime'ı byte array olarak al
        w_prime_bytes = self.get_bytes(w_prime)
        
        # Bu simülasyonda BCH'yi w_prime'ın gürültüsünü temizlemek için kullanıyoruz.
        # Gerçek hayatta w ^ c saklanır, w' ^ (w^c) = c' elde edilir, sonra decode(c') -> c.
        
        fixed_w, flips = self.bch_handler.decode(w_prime_bytes, P['ecc'])
        
        if flips >= 0:
            # Başarılı düzeltme
            R = self.derive_key(fixed_w, P['salt'])
            return R, flips
        else:
            return None, -1

    def get_bytes(self, data):
        if isinstance(data, str):
            return data.encode()
        return bytes(data)

    def derive_key(self, w, salt):
        hasher = hashlib.sha256()
        hasher.update(w)
        hasher.update(salt)
        return hasher.hexdigest()

if __name__ == "__main__":
    # Basit test
    fe = FuzzyExtractor()
    bio_data = os.urandom(128) # 1024 bit
    
    print("[GEN] Kayıt yapılıyor...")
    R1, P = fe.gen(bio_data)
    print(f"[GEN] Üretilen Anahtar: {R1[:16]}...")
    
    # Gürültü ekle
    add_noise = bch_module.add_noise
    
    noisy_bio = add_noise(bio_data, 10) # 10 bit hata
    print("[SIM] 10 bit gürültü eklendi.")
    
    print("[REP] Doğrulama yapılıyor...")
    R2, flips = fe.rep(noisy_bio, P)
    
    if R1 == R2:
        print(f"[REP] Başarılı! {flips} bit hata düzeltildi.")
        print(f"[REP] Anahtar eşleşti: {R2[:16]}...")
    else:
        print("[REP] Başarısız! Anahtarlar eşleşmedi.")
