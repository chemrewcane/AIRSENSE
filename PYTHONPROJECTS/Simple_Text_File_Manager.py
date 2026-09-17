print("--- SIMPLE NOTES MANAGER ---")

while True:
    print("\n1. Add Note")
    print("2. View Notes")
    print("3. Search Note")
    print("4. Exit")

    choice = input("\nChoose an option: ")

    if choice == "1":
        note = input("\nEnter note: ")
        with open("notes.txt", "a") as file:
            file.write(note + "\n")
        print("Note saved successfully.")

    elif choice == "2":
        try:
            with open("notes.txt", "r") as file:
                notes = file.readlines()
                if notes:
                    print("\n--- SAVED NOTES ---\n")
                    for note in notes:
                        print(note.strip())
                else:
                    print("No notes have been saved yet.")
        except FileNotFoundError:
            print("No notes have been saved yet.")

    elif choice == "3":
        search_term = input("\nEnter word to search: ")
        try:
            with open("notes.txt", "r") as file:
                notes = file.readlines()
                found_notes = [note.strip() for note in notes if search_term.lower() in note.lower()]
                if found_notes:
                    print("\nMatching Notes:")
                    for note in found_notes:
                        print(note)
                else:
                    print("No matching note found.")
        except FileNotFoundError:
            print("No notes have been saved yet.")

    elif choice == "4":
        print("Exiting Note Manager. Goodbye!")
        break

    else:
        print("Invalid choice. Please enter a number between 1 and 4.")