from postcode import simple_chat, setup_chroma


def main():
    chroma_collection_manager = setup_chroma()
    simple_chat(chroma_collection_manager)


if __name__ == "__main__":
    main()
