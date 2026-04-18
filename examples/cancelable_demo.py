import sys
import os
import importlib.util
from rich.console import Console
from rich.table import Table

console = Console()

def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

cb_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '04_Guvenlik_ve_Gizlilik', 'cancelable.py'))
cb_module = import_module_from_path('cancelable', cb_path)
CancelableBiometrics = cb_module.CancelableBiometrics

def run_demo():
    console.print("\n[bold blue]🛡️ Cancelable Biometrics (İptal Edilebilir Biyometrik Şablonlar) Demo[/bold blue]\n")
    
    cb = CancelableBiometrics(seed=1337)
    
    # Orijinal Biyometrik Veri (Örneğin parmak izi öznitelikleri)
    original_template = b"FINGERPRINT_MINUTIAE_XY_DATA_USER01"
    console.print(f"[cyan][+][/cyan] Orijinal Şablon: [white]{original_template.decode()}[/white]")
    
    # Senaryo: Kullanıcı uygulamaya kaydolur (Token A ile)
    token_a = "user_private_token_alpha"
    template_a = cb.salt_template(original_template, token_a)
    
    # Senaryo: Kullanıcı sızıntıdan sonra şablonunu iptal eder ve yeni bir token alır (Token B)
    token_b = "user_private_token_beta"
    template_b = cb.salt_template(original_template, token_b)
    
    # Tablo ile Karşılaştır
    table = Table(title="Şablon İptal Edilebilirlik Analizi")
    table.add_column("Şablon", style="yellow")
    table.add_column("Token", style="magenta")
    table.add_column("Türetilen Değer (Hex)", style="green", no_wrap=True)
    
    table.add_row("Şablon A", "Alpha", template_a.hex()[:32] + "...")
    table.add_row("Şablon B", "Beta", template_b.hex()[:32] + "...")
    
    console.print(table)
    
    if template_a != template_b:
        console.print("\n[bold green]✓ Güvenli![/bold green] Aynı biyometrik veri farklı tokenlar ile tamamen farklı şablonlar üretti.")
        console.print("[white]Eğer Şablon A çalınırsa, kullanıcı Şablon B'ye geçerek güvenliğini sağlayabilir.[/white]\n")

    # BioHash Gösterimi
    console.print("[bold cyan][+][/bold cyan] BioHashing Uygulanıyor (Rastgele Projeksiyon)...")
    bio_hash, _ = cb.bio_hash(original_template)
    console.print(f"BioHash (İlk 64 bit): [bold yellow]{''.join(map(str, bio_hash[:64]))}[/bold yellow]\n")

if __name__ == "__main__":
    run_demo()
