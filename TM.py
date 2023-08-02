import re
import requests

class Transfer():
  def __init__(self, age, theor_cost, real_cost):
    self.age = int(age)
    self.theor_cost = float(theor_cost)
    self.real_cost = float(real_cost)
    self.real_to_theor = self.real_cost / self.theor_cost
    self.cluster = -1


  def __repr__(self):
    return str(self.age) + '-летний оценён в: ' + str(self.theor_cost) + ' млн €, перешёл за ' + str(self.real_cost) + ' млн €.'

class MyTMParser():
    def __init__(self):
      self.url_base = 'https://www.transfermarkt.world/transfers/saisontransfers/statistik?ajax=yw0&altersklasse=&ausrichtung=&land_id=0&leihe=&saison-id=0&spielerposition_id=&transferfenster=sommertransfers&page='
      self.n = 18
      self.raw = [False for i in range(self.n)]


    def get_raw_page(self, i, force_upd=False):
      if not self.raw[i] or force_upd:
        response = requests.get(self.url_base + str(i + 1), headers={'User-Agent': 'Custom'})
        print('HTTP response: ', response)
        self.raw[i] = response.text
  
      return self.raw[i]


    def get_raw_transfers(self, i):
      group_matches = re.findall(r'(([ \t]*)<tr .*?[^ \t]\2</tr>)', self.get_raw_page(i), re.DOTALL)
      return [x[0] for x in group_matches]


    def parse_cost(self, raw):
      cost_match = re.match('^(\d+)(?:|,(\d+)) (млн|тыс)', raw)
      if not cost_match:
        return 0

      cost = float(cost_match.group(1))
      print(raw)
      if cost_match.group(2):
        cost += float('0.' + cost_match.group(2))

      if cost_match.group(3) == 'тыс':
        cost = cost / 1000

      return cost


    def get_transfer(self, raw):
      raw_items = raw.split('</td><')[:-1]
      raw_list = [re.search('>([^>]*$)', s).group(1) for s in raw_items]
      age = int(raw_list[2])
      theor_cost = self.parse_cost(raw_list[3])
      real_cost = self.parse_cost(raw_list[6])
      if min(theor_cost, real_cost) == 0:
        return None
      return Transfer(age, theor_cost, real_cost)



    def get_transfers(self):
      transfer_list = []
      for i in range(self.n):
        transfer_list += [self.get_transfer(x) for x in self.get_raw_transfers(i)]

      # remove free agents & loans
      transfer_list = [x for x in transfer_list if x]
      return transfer_list

      
parser = MyTMParser()
transfers = parser.get_transfers()
print(transfers[0])
