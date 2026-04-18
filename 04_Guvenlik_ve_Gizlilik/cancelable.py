import hashlib
import numpy as np

class CancelableBiometrics:
    """
    Cancelable Biometrics (İptal Edilebilir Biyometri) Sınıfı.
    Biyometrik veriyi geri döndürülemez bir dönüşümden geçirerek şablonu korur.
    """
    def __init__(self, seed=None):
        self.seed = seed

    def salt_template(self, template, token):
        """
        Salting (Tuzlama) — Biyometrik şablonu bir token/anahtar ile karmaşıklaştırır.
        """
        if isinstance(template, str):
            template = template.encode()
        
        # Basit bir XOR salting simülasyonu
        # Gerçek uygulamalarda permutasyon veya non-linear dönüşümler kullanılır.
        token_hash = hashlib.sha256(str(token).encode()).digest()
        
        # Template ve token hash'i XOR'la (template boyutuna uydurarak)
        result = bytearray()
        for i in range(len(template)):
            result.append(template[i] ^ token_hash[i % len(token_hash)])
            
        return bytes(result)

    def bio_hash(self, template, projection_matrix=None):
        """
        BioHashing — Rastgele projeksiyon kullanarak şablonu dönüştürür.
        """
        # template'i sayısal bir vektöre çevirelim
        # varsayılan: template byte array'dir
        vec = np.frombuffer(template, dtype=np.uint8).astype(float)
        
        if projection_matrix is None:
            # Rastgele bir projeksiyon matrisi oluştur
            np.random.seed(self.seed)
            projection_matrix = np.random.randn(len(vec), len(vec))
        
        # Projeksiyon (Matrix Multiplication)
        transformed = np.dot(projection_matrix, vec)
        
        # Eşikleme (Thresholding) -> Binary şablon
        bio_hash_result = (transformed > 0).astype(int)
        
        return bio_hash_result, projection_matrix

if __name__ == "__main__":
    cb = CancelableBiometrics(seed=42)
    original_bio = b"user_fingerprint_data_123"
    
    print(f"[ORIG] Orijinal Veri: {original_bio}")
    
    # Token 1 ile şablon oluştur
    t1 = cb.salt_template(original_bio, "token_alpha")
    print(f"[T1] Şablon 1 (Alpha): {t1.hex()[:20]}...")
    
    # Token 2 ile şablon oluştur (İptal edilebilir özellik)
    t2 = cb.salt_template(original_bio, "token_beta")
    print(f"[T2] Şablon 2 (Beta):  {t2.hex()[:20]}...")
    
    if t1 != t2:
        print("[OK] Farklı tokenlar farklı şablonlar üretti. Biyometri iptal edilebilir (cancelable) durumda.")
    
    # BioHashing Testi
    bio_hash_v1, matrix = cb.bio_hash(original_bio)
    print(f"[BH] BioHash (İlk 10 bit): {bio_hash_v1[:10]}")
