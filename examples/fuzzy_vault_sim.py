import sys
import os
import importlib.util
from rich.console import Console
from rich.panel import Panel

console = Console()

def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

fe_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '03_Fuzzy_Extractor', 'fuzzy_extractor.py'))
fe_module = import_module_from_path('fuzzy_extractor', fe_path)
FuzzyExtractor = fe_module.FuzzyExtractor

bch_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '02_Hata_Duzeltme_Kodlari', 'bch_handler.py'))
bch_module = import_module_from_path('bch_handler', bch_path)
add_noise = bch_module.add_noise

def run_simulation():
    console.print(Panel.fit("🔮 [bold white]Canlı Anahtar — Fuzzy Extractor Simülasyonu[/bold white]", style="purple"))
    
    fe = FuzzyExtractor(n=1024, t=60)
    
    # 1. Kayıt Aşaması
    bio_data = os.urandom(128) # 1024 bitlik parmaka izi özeti
    console.print(f"\n[bold cyan][GEN][/bold cyan] [white]Biyometrik Kayıt Yapılıyor...[/white]")
    R1, P = fe.gen(bio_data)
    console.print(f"[bold cyan][GEN][/bold cyan] [green]Anahtar (R) Üretildi:[/green] {R1}")
    console.print(f"[bold cyan][GEN][/bold cyan] [yellow]Helper Data (P) Saklandı.[/yellow]")
    
    # 2. Gürültü Simülasyonu
    noise_percent = 0.05
    noise_bits = int(1024 * noise_percent)
    noisy_bio = add_noise(bio_data, noise_bits)
    console.print(f"\n[bold yellow][SIM][/bold yellow] [white]%5 gürültü ekleniyor... ({noise_bits} bit flip)[/white]")
    
    # 3. Yeniden Üretme Aşaması
    console.print(f"\n[bold magenta][REP][/bold magenta] [white]Doğrulama ve Yeniden Üretme Başlatıldı...[/white]")
    R2, flips = fe.rep(noisy_bio, P)
    
    if R2 and R1 == R2:
        console.print(f"[bold magenta][REP][/bold magenta] [green]BCH Decode Başarılı — {flips} bit hata düzeltildi.[/green]")
        console.print(f"[bold magenta][REP][/bold magenta] [bold green]Anahtar Eşleşti! ✓[/bold green] {R2}")
    else:
        console.print(f"[bold magenta][REP][/bold magenta] [bold red]Hatalı Biyometrik Veri veya Çok Fazla Gürültü. Anahtar Kurtarılamadı.[/bold red]")

if __name__ == "__main__":
    run_simulation()
