import sys
import os

# Root dizini ekle
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
add_noise = bch_module.add_noise
from rich.console import Console
from rich.table import Table

console = Console()

def run_demo():
    console.print("\n[bold cyan]🔑 BCH Hata Düzeltme Kodları Demo[/bold cyan]\n")
    
    # BCH(1024, t=50) simülasyonu
    h = BCHHandler(n=1024, t=50)
    
    # Orijinal Veri
    original_data = b"Biyometrik Veri: Parmak Izi Ozellikleri v1.0"
    console.print(f"[green][+][/green] Orijinal Veri: [white]{original_data.decode()}[/white]")
    
    # Encode
    ecc = h.encode(original_data)
    console.print(f"[green][+][/green] ECC (Hata Düzeltme Bitleri) üretildi. Boyut: {len(ecc)} byte")
    
    # Gürültü Ekle
    noise_count = 35
    noisy_data = add_noise(original_data, noise_count)
    console.print(f"[yellow][!][/yellow] {noise_count} bit rastgele hata eklendi.")
    
    # Decode / Correct
    fixed_data, flips = h.decode(noisy_data, ecc)
    
    # Sonuçları Tabloyla Göster
    table = Table(title="BCH Düzeltme Sonuçları")
    table.add_column("Özellik", style="cyan")
    table.add_column("Değer", style="magenta")
    
    table.add_row("Düzeltme Kapasitesi (t)", str(h.t))
    table.add_row("Eklenen Hata", str(noise_count))
    table.add_row("Düzeltilen Bit Sayısı", str(flips))
    table.add_row("Başarı Durumu", "✅ BAŞARILI" if flips >= 0 else "❌ BAŞARISIZ")
    
    console.print(table)
    
    if fixed_data == original_data:
        console.print("\n[bold green]✓ Veri orijinal haline başarıyla döndürüldü![/bold green]\n")
    else:
        console.print("\n[bold red]✗ Veri kurtarılamadı. Hata sayısı kapasiteyi aşmış olabilir.[/bold red]\n")

if __name__ == "__main__":
    run_demo()
