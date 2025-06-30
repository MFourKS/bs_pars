def count_matches(test_file="test_id.txt", product_file="product_ids.txt"):
    with open(test_file, "r", encoding="utf-8") as f:
        test_ids = set(line.strip() for line in f if line.strip())

    with open(product_file, "r", encoding="utf-8") as f:
        product_ids = set(line.strip() for line in f if line.strip())

    matched_ids = test_ids.intersection(product_ids)
    print(f"Совпадений найдено: {len(matched_ids)} из {len(test_ids)}")

    if matched_ids:
        print("Совпадающие:")
        for mid in matched_ids:
            print(mid)

if __name__ == "__main__":
    count_matches()
