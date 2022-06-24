import re
class SortGet_prob:
    def sort_key(ans):
        get_prob = ans['m.get_prob']
        key = []
        index = get_prob.find('%')
        if index != -1:
            for i in reversed(get_prob)[1:]:
                if i.isdigit:
                    key += i
                else:
                    break
            key = reversed(key)
        else:
            key = get_prob
        
        return key

    def cmp(a,b):
        if (not(a.isdigit) and not(b.isdigit)) or (a.isdigit and b.isdigit):
                return (a - b)
        else:
            if a.isdigit:
                return -1
            else:
                return 1
        
        
if __name__ == '__main__':
    sortfunc = SortGet_prob()
        