from agent import run_agent
from database.schemas import UserRole


def main():

    print("=" * 60)
    print("SIMPLE SHOPPING AGENT")
    print("=" * 60)


    role_input = input(
        "\nChoose role (customer/admin): "
    ).strip().lower()

    if role_input == "admin":
        role = UserRole.ADMIN
    else:
        role = UserRole.CUSTOMER

    print(f"\nLogged in as: {role.value}")

    print("\nYou can now chat with the Shopping Agent.")
    print("Type 'exit' or 'quit' to stop the program.")

    # -----------------------------------------------------
    # Conversation Loop
    # -----------------------------------------------------

    while True:

        print("\n" + "-" * 60)

        user_request = input(
            f"{role.value}> "
        ).strip()

        # Empty input
        if not user_request:
            continue

        # Exit application
        if user_request.lower() in ["exit", "quit"]:
            print("\nShopping Agent stopped.")
            break

        # Run agent
        try:

            run_agent(
                user_request=user_request,
                user_role=role,
            )

        except KeyboardInterrupt:

            print("\n\nShopping Agent stopped.")
            break

        except Exception as error:

            print(
                f"\n[ERROR] Something went wrong: {error}"
            )


if __name__ == "__main__":
    main()