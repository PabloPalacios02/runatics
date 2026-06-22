from services.supabase_service import get_supabase_client

supabase = get_supabase_client()

print("Conectado")

res = supabase.table("profiles").select("*").execute()

print(res.data)
