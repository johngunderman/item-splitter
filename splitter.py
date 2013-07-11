""" Basic splitter interface """
import mwmatching
from pprint import pprint

class Bid(object):
    def __init__(self, item, actor, amount):
        self.item = item
        self.actor = actor
        self.amount = amount

    def __eq__(self, other):
        return self.item   == other.item  and \
               self.actor  == other.actor and \
               self.amount == other.amount

    def __repr__(self):
        return "Bid(" + str(self.item) + ", " + str(self.actor) + \
                ", " + str(self.amount) + ")"

class Splitter(object):
    def calc_averages(self, items, bids):
        averages = {}
        for item in items:
            bids_for_item = [bid.amount for bid in bids if bid.item == item]
            if len(bids_for_item) > 0:
                averages[item] = float(sum(bids_for_item)) / len(bids_for_item)
            else:
                averages[item] = 0
        return averages

    def split(self, items, actors, bids, exclusive=True):
        print "Attempting to split:"
        print "== Items: "
        pprint(items)
        print "== between:"
        pprint(actors)
        print "== as per the bids:"
        pprint(bids)
        averages = self.calc_averages(items, bids)
        bid_dict = {}
        for bid in bids:
            bid_dict[(bid.item, bid.actor)] = bid

        edges = []
        for i in range(len(items)):
            for j in range(len(actors)):
                if (items[i], actors[j]) in bid_dict:
                    bid = bid_dict[(items[i], actors[j])]
                    edges.append((i, len(items) + j, self.score(bid, averages)))

        mw = mwmatching.maxWeightMatching(edges)
        result = {}
        unused_actors = actors[:]
        unused_items = items[:]
        for i in range(len(items)):
            if mw[i] != -1:
                winner = actors[mw[i] - len(items)]
                result[items[i]] = (winner, bid_dict[(items[i], winner)].amount)
                unused_actors.remove(winner)
                unused_items.remove(items[i])
            else:
                result[items[i]] = None


        # This isn't really ideal, but this code is meant to handle the case
        # where not all bids can be satisfied. The max-weight solution will
        # force someone into a room at a different price than they bid.
        # In my tests, it seems to always be a lower price, but I'm not counting
        # on that.
        #
        # Example input that causes this issue (5 person / 5 item auction):
        #
        # 1640, 1540, 1140, 1640, 1740
        # 1540, 1240, 1340, 1640, 1940
        # 1740, 1540, 1040, 1640, 1740
        # 1440, 1640, 1240, 1640, 1740
        # 1640, 1640, 1140, 1640, 1640
        total_dollars = sum([bid.amount for bid in bids if bid.actor == actors[0]])
        amount_spent = sum([v[1] for k,v in result.items() if v is not None])
        remaining_amount = total_dollars - amount_spent
        remaining_per_item = remaining_amount / len(unused_items)
        if unused_actors:
            print "Warning: could not properly satisfy auction."
            for k,v in result.items():
                if v is None:
                    result[k] = (unused_actors, remaining_per_item)

        return result

    def score(self, bid, averages):
        return bid.amount



