from emulation import emulation
from servers.Neo4jServer import Neo4jServer

def print_list(name_of_list, list):
    print(name_of_list)
    count = 1
    for item in list:
        print(f"{count}: {item}")
        count += 1

def print_path(name_of_path, path):
    print(name_of_path)
    way = ""
    for node in path:
        way += f"{node} -> "
    print(way[:-3])


def neo4j_menu():

    server = Neo4jServer()

    print("\n1. Find all users that sent or received messages with a set of tags")
    print("2. Find all pairs of connected users length N through sent or received messages")
    print("3. Find on the graph the shortest path between users through sent or received messages")
    print("4. Find authors of messages that are only related to each other messages marked as spam")
    print("5. Find all users that sent or received messages with a set of tags, but these users are not connected")
    print("0. Exit")

    choice = int(input("\nChoose option: "))

    if choice == 1:
        tags = input("Enter tags (work, advertisement, notification) separated by comma: ")
        users = server.get_users_with_tagged_messages(tags)
        print_list("\nUsers: ", users)

    elif choice == 2:
        n = input("Enter n: ")
        users = server.get_users_with_n_long_relations(n)
        print_list("\nPairs of users: ", users)

    elif choice == 3:
        print(server.get_users())

        username1 = input("\nEnter username1: ")
        username2= input("Enter username2: ")
        path = server.shortest_way_between_users(username1, username2)

        print_path("\nPath:", path)

    elif choice == 4:
        users = server.get_users_which_have_only_spam_conversation()
        print_list("\nSpam related users: ", users)

    elif choice == 5:
        tags = input("Enter tags (work, advertisement, notification) separated by comma: ")
        users = server.get_unrelated_users_with_tagged_messages(tags)
        print_list("\nGroups of unrelated users: ", users)



def main():
    print("\tMain menu")
    print("1. Neo4j menu")
    print("2. Emulation")
    print("0. Exit")

    choice = int(input("\nChoose option: "))

    if choice == 1:
        neo4j_menu()
    elif choice == 2:
        emulation()


if __name__ == "__main__":
    main()