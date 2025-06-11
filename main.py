from data_extraction import get_top_player_ids, get_kona_player_info, extract_stats, print_stats_table

def main():
    top_ids = get_top_player_ids()

    kona_data = get_kona_player_info()

    df = extract_stats(kona_data, top_ids)

    print_stats_table(df)

if __name__ == "__main__":
    main()