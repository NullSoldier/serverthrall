from collections import OrderedDict


class ConanConfigDict(OrderedDict):

    def __setitem__(self, key, value):
        if key in self and isinstance(value, list):
            item = self.__getitem__(key)
            item.extend(value)
        else:
            super(ConanConfigDict, self).__setitem__(key, value)

    def items(self, *args, **kwargs):
        result = []
        inner_items = super(ConanConfigDict, self).items(*args, **kwargs)

        for key, value in inner_items:
            if not isinstance(value, list):
                result.append((key, value))
            else:
                for subvalue in value:
                    result.append((key, subvalue))

        return result
