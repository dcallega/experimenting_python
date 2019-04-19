from copy import deepcopy

def find_all_subsets(l):
  ret = [[]]
  for e in l:
    tmp = deepcopy(ret)
    for k in tmp:
      ret.append(k + [e])
  return ret






if __name__ == "__main__":
  test = [1,2,3,4,5,9]
  print(len(find_all_subsets(test)) == 2**len(test))

