import CustomVrChatAPI, pickle, re
from os.path import exists

class AvatarGroups:

    def __init__(self):
        self.groups = []
        self.__load()
        self.api = None
        
    # This method sets the api.
    # api: (VRCAPI) api
    def setAPI(self, api):
        self.api = api

    # This method gets the api
    # Returns: (VRCAPI) api
    def getAPI(self):
        return self.api
    
    # This method gets the group with given name. Returns None if the group doesn't exist
    # group_name: (String) name of the group
    # returns: (Group) group
    def getGroup(self, group_name):
        group = next((x for x in self.groups if x.name == group_name), None)
        if not group:
            print("No group with the given name found")
            return None
        else:
            return group

    # This method saves all the currently favorited avatars to the indicated group
    # group_name: (String) name of the group
    # returns: (Boolean) successful
    def saveAvatar(self, group_name):
        # Check if the api is set
        if not self.api:
            print("Please login first!")
            return False

        # Get target group
        group = self.getGroup(group_name)
        if not group:
            print("The group with the given group name not found")
            return False
        
        fav_avatars = self.api.get("/avatars/favorites", {"offset": 0, "n": 100})
        fav_avatars.raise_for_status()
        print("fav_avatars return code: " + str(fav_avatars.status_code))

        group.clearData()
        if fav_avatars.status_code == 200:
                data = fav_avatars.json()
                print("data len: " + str(len(data)))
                for i in range(len(data)):
                    group.addAvatar(data[i])

        # Save the data to local file
        self.__save()

        print("All avatars saved!")
        return True

    # This method unfavorites the avatar with given id
    # favoriteId: (String) favorite id
    # returns: (Boolean) successful
    def __unfavoriteAvatar(self, favoriteId):
        # Check if the api is set
        if not self.api:
            print("Please login first!")
            return False

        r = self.api.delete("/favorites/" + favoriteId)
        #r.raise_for_status()
        return r.status_code == 200

    # This method favorites the avatar with given id
    # avatarId: (String) avatar id
    # returns: (Boolean) successful
    def __favoriteAvatar(self, avatarId):
        # Check if the api is set
        if not self.api:
            print("Please login first!")
            return False

        r = self.api.post("/favorites", {"type": "avatar", "favoriteId": avatarId, "tags": ["avatars1"]})
        #r.raise_for_status()
        return r.status_code == 200

    # This method switches the current favorites to target group and stores all the current favorites
    # to the backup group
    # target_group_name: (String) target group name
    # backup_group_name: (String) backup group name
    # returns: (Boolean) successful
    def switchGroup(self, target_group_name, backup_group_name):
        if not self.saveAvatar(backup_group_name):
            print("Something went wrong when saving current group to backup group")
            return False

        # Get the backup group and remove all the avatars from favorite
        self.unloadGroup(backup_group_name)
        
        # Add avatars from target group to favorites
        self.loadGroup(target_group_name)
        return True


    # This method unfavorites all the avatars which is in the indicated group
    # group_name: (String) group name
    # returns: (Boolean) successful
    def unloadGroup(self, group_name):
        group = self.getGroup(group_name)
        if not group:
            print("The group with the given group name not found")
            return False

        print("Unloading current favorites...Please wait...")
        for data in group.getAvatars():
            #avatar = data.json()
            favoriteId = data["favoriteId"]
            if not self.__unfavoriteAvatar(favoriteId):
                print("Something went wrong while removing avatars from favorite: " + favoriteId)

        print("Unloading complete.")
        return True


    # This method favorites all the avatars which is in the indicated group
    # group_name: (String) group name
    # returns: (Boolean) successful
    def loadGroup(self, group_name):
        group = self.getGroup(group_name)
        if not group:
            print("The group with the given group name not found")
            return False

        print("Loading avatars from group " + group_name + ", Please wait...")
        for data in group.getAvatars():
            #avatar = data.json()
            avatarId = data["id"]
            if not self.__favoriteAvatar(avatarId):
                print("Something went wrong while adding avatars to favorite: " + avatarId)
        print("Loading complete")
        return True


    # This method creates a new group with given name
    # group_name: (String) group name
    # returns: (Group) newly created group
    def newGroup(self, group_name):
        group = next((x for x in self.groups if x.name == group_name), None)
        if group:
            print("There's already a group with the given name in groups")
            return None
        else:
            retval = Group(group_name)
            self.groups.append(retval)
            print("New group has successfully been added to groups")

            # Save the data to local file
            self.__save()

            return retval


    # This method deletes a group with given name
    # group_name: (String) group name
    # returns: (Boolean) successful
    def delGroup(self, group_name):
        group = next((x for x in self.groups if x.name == group_name), None)
        if group:
            self.groups.remove(group)

            # Save the data to local file
            self.__save()
            return True
        else:
            print("Group with name " + group_name + " doesn't exist")
            return False

    # This method lists all the groups
    def listGroup(self):
        for group in self.groups:
            print("Group name: " + group.name + ", Num. of avatars: " + str(len(group.avatars)))

    # This method serializes all the groups into a string
    # Returns: (String) serialized groups
    def __encodeGroups(self):
        if len(self.groups) == 0:
            print("There're currently no group")
            return None
        else:
            return pickle.dumps(self.groups)
        

    # This method saves the serialized groups into a local file
    def __save(self):
        with open("favorite_data.dat", "wb") as f:
            f.write(self.__encodeGroups())
            f.close()


    # This method loads the serialized groups from a local file
    def __load(self):
        # Check if the data file exists
        if not exists("favorite_data.dat"):
            return

        data = b""
        with open("favorite_data.dat", "rb") as f:
            data += f.read()
            f.close()

        if data:
            self.groups = pickle.loads(data)


    # This method clears the local file
    # Note: All the locally stored data will be lost
    def clearData(self):
        with open("favorite_data.dat", "wb") as f:
            f.write(b"")
            f.close()
        self.groups = []


class Group:
    def __init__(self, name):
        self.name = name
        self.avatars = []

    def addAvatar(self, avatar):
        self.avatars.append(avatar)

    def clearData(self):
        self.avatars = []

    def getAvatars(self):
        return self.avatars


def main():
    avatar_groups = AvatarGroups()

    while True:
        print("Command: ", end='')
        cmd = input()
        args = cmd.split()

        if cmd == "exit":
            break
        if args[0] == "help":
            print("Commands are listed below: ")
            print("     login <username> <password>: login to your account")
            print("     group list: list all avatar groups")
            print("     group delete <group_name>: delete an avatar group")
            print("     group create <group_name>: create a new avatar group")
            print("     group save <group_name>: save current favorite avatars to the group")
            print("     group switch <group_name> <backup_group_name>: load favorite avatars from the group, stores "
            + "current favorite avatars to backup group")
            print("     group load <group_name>: load favorite avatars from the group")
            print("     group clear: clear all locally saved data")
            print("     help: get help")
            print("     exit: exit the program")
            continue
        elif args[0] == "group":
            
            # Use a little regex to check if the input is valid
            if not re.match(r"list|clear|delete|create|save|load|switch", args[1]):
                print("Invalid command, please use help command to get help!")
                continue

            if args[1] == "list":
                avatar_groups.listGroup()
            elif args[1] == "clear":
                avatar_groups.clearData()
            else:
                # Check if the name of the group is indicated
                if len(args) <= 2:
                    print("Invalid command, please use help command to get help")
                    continue
                
                group_name = args[2]
                
                if args[1] == "delete":
                    avatar_groups.delGroup(group_name)
                if args[1] == "create":
                    avatar_groups.newGroup(group_name)
                if args[1] == "save":
                    avatar_groups.saveAvatar(group_name)
                if args[1] == "load":
                    avatar_groups.loadGroup(group_name)
                if args[1] == "switch" and len(args) == 4:
                    avatar_groups.switchGroup(group_name, args[3])
        elif args[0] == "login" and len(args) == 3:
            api = CustomVrChatAPI.VRCAPI(username=args[1], password=args[2])
            avatar_groups.setAPI(api)
        else:
            print("Invalid command, please use help command to get help")




if __name__ == "__main__":
    main()