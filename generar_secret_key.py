import secrets

print("=" * 60)
print("🔐 GENERADOR DE CLAVE SECRETA PARA FLASK")
print("=" * 60)
print("\nCopia esta clave y úsala como FLASK_SECRET_KEY en Render:\n")
print(f"FLASK_SECRET_KEY = {secrets.token_hex(32)}")
print("\n" + "=" * 60)
print("✅ ¡Guarda esta clave de forma segura!")
print("=" * 60)
