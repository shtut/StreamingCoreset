class Stack:
    def __init__(self):
        self.items = []  # You don't want to assign [] to self - when you do that, you're just assigning to a new local variable called `self`.  You want your stack to *have* a list, not *be* a list.

    def is_empty(self):
        return self.size() == 0  # While there's nothing wrong with self.container == [], there is a builtin function for that purpose, so we may as well use it.  And while we're at it, it's often nice to use your own internal functions, so behavior is more consistent.

    def push(self, item):
        self.items.append(item)  # appending to the *container*, not the instance itself.

    def pop(self):
        return self.items.pop()  # pop from the container

    def size(self):
        return len(self.items)  # length of the container

    def top(self):
        return self.items[len(self.items) - 1]  # return last element