def Solution_sorted(l, t):
  one, two = 0, len(l)-1
  while(two > one):
    tmp = l[one] + l[two]
    if tmp == t:
      return True
    elif tmp < t:
      one += 1 
    else:
      two -= 1
  return False

def Solution_unsorted(l, t):
  comp = set()
  for e in l:
    # print(e, t-e, comp)
    if (t-e) in comp:
      return True
    else:
      comp.add(e)
  return False

if __name__ == "__main__":
  print(Solution_unsorted([1,3,5,6,9], 11))
  print(Solution_unsorted([1,3,5,6,9], 10))
  print(Solution_unsorted([1,3,5,6,9], 13))
  print(Solution_unsorted([1,3,5,6,9], 8))
  print(Solution_unsorted([1,3,5,6,9], 0))
