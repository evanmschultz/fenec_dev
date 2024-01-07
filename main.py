from postcode import (
    simple_chat,
    setup_chroma,
    update_all_with_graph_db,
    ChromaCollectionManager,
)


def main() -> None:
    # chroma_collection_manager: ChromaCollectionManager = update_all_with_graph_db()
    chroma_collection_manager = setup_chroma()
    simple_chat(chroma_collection_manager)


if __name__ == "__main__":
    main()
