from src.database import create_users_table


def main():
    print("Creating database tables...")

    create_users_table()

    print("Users table created successfully.")


if __name__ == "__main__":
    main()