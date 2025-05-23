import pandas as pd

# CSV'yi oku
df = pd.read_csv("output/detailed_data.csv")

# Fiyatı önce stringe çevir, sonra işle
df["price"] = df["price"].astype(str).str.replace(" TL", "", regex=False).str.replace(",", ".")

# Geçerli float değerleri al
df["price"] = pd.to_numeric(df["price"], errors="coerce")

# Geçerli fiyatları filtrele
df_valid = df.dropna(subset=["price"])

# En ucuz 5
cheapest = df_valid.sort_values("price").head(5)

# En pahalı 5
most_expensive = df_valid.sort_values("price", ascending=False).head(5)

print("En Ucuz 5 Satıcı:\n", cheapest[["product_name", "seller", "price", "rating", "shipping"]], end="\n\n")
print("En Pahalı 5 Satıcı:\n", most_expensive[["product_name", "seller", "price", "rating", "shipping"]])
