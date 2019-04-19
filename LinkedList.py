class Node:
  def __init__(self, v, n=None):
    self.value = v
    self.next = n


class LinkedList:
  def __init__(self, n=None):
    if type(n) == type(Node(0,None)):
      self.head = n
    else:
      self.head = Node(n)

  def add(self, v=None, pos=-1):
    n = self.head
    curr_pos = 1
    if pos == 0:
      self.head = Node(v, n)
    else:
      while(n.next is not None and curr_pos != pos):
        n = n.next
        curr_pos += 1
      tmp = n.next
      n.next = Node(v, tmp)
    return self

  def list_elements(self):
    n = self.head
    ret = []
    while(n is not None):
      ret.append(n.value)
      n = n.next
    return ret

  def print_elements(self):
    print(l.list_elements())

  def remove(self, pos):
    n = self.head
    if pos == 0:
      self.head = self.head.next
    else:
      curr_pos = 0
      prev = None
      while(n.next is not None and curr_pos != pos):
        prev = n
        n = n.next
        curr_pos += 1
      if curr_pos != pos:
        raise ValueError("Cannot remove element {} in list with length {}".format(pos, curr_pos+1))
      else:
        ret = n.value
        prev.next = n.next
        return ret



if __name__=="__main__":
  l = LinkedList(2)
  l.add(3).add(0, 0).add(1, 1)
  l.print_elements()
  l.remove(4)
  l.print_elements()






  