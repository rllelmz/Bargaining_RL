import random
from pade.acl import aid
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.behaviours.protocols import Behaviour
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID


class Vendeur(Agent):
    def __init__(self, aid):
        super(Vendeur, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Je suis le Vendeur')
        self.prix_initial = random.randrange(200, 1600)
        self.prix_reserve = int(self.prix_initial * 0.5)
        self.client = "null"

    def initialize_send(self):
        vendeur_behaviour = VendeurBehaviour(self)
        self.behaviours.append(vendeur_behaviour)
        vendeur_behaviour.on_start()


class VendeurBehaviour(Behaviour):
    def __init__(self, agent):
        super().__init__(agent)
        self.proposition = self.agent.prix_initial

    def on_start(self):
        message = ACLMessage(ACLMessage.CFP)
        message.add_receiver(self.agent.client)
        message.set_content(str(self.proposition))
        self.agent.send(message)
        msg = 'Prix initial [' + str(self.proposition) + '] envoyé à: {}'.format(self.agent.client)
        display_message(self.agent.aid.name, msg)

    def generate_proposition(self, precedente_valeur):
        return random.randrange(precedente_valeur, self.agent.prix_initial)

    def execute(self, message):
        if message.performative == ACLMessage.PROPOSE:
            msg = 'J\'ai reçu la proposition [' + message.content + '] de : {}'.format(message.sender.name)
            display_message(self.agent.aid.name, msg)
            precedente_valeur = int(message.content)
            if precedente_valeur < self.agent.prix_reserve:
                # Envoyer un refus
                rejection = ACLMessage(ACLMessage.REJECT_PROPOSAL)
                self.agent.send(rejection)
                msg = 'Proposition [' + str(precedente_valeur) + '] refusée.'
                display_message(self.agent.aid.name, msg)
                self.proposition = self.generate_proposition(precedente_valeur)
                proposal = ACLMessage(ACLMessage.CFP)
                proposal.add_receiver(self.agent.client)
                proposal.set_content(str(self.proposition))
                self.agent.send(proposal)
                msg = 'Proposition [' + str(self.proposition) + '] envoyée à: {}'.format(self.agent.client)
                display_message(self.agent.aid.name, msg)
            else:
                # Accepter une offre d'un client
                acceptation = ACLMessage(ACLMessage.ACCEPT_PROPOSAL)
                acceptation.set_content(str(precedente_valeur))
                self.agent.send(acceptation)
                msg = 'Proposition [' + str(precedente_valeur) + '] acceptée de : {}'.format(self.agent.client)
                display_message(self.agent.aid.name, msg)
                self.agent.behaviours.remove(self)
        if message.performative == ACLMessage.ACCEPT_PROPOSAL:
            display_message(self.agent.aid.name, "Négociation terminée")
            self.agent.behaviours.remove(self)
        if message.performative == ACLMessage.REJECT_PROPOSAL:
            display_message(self.agent.aid.name, "REJECT PROPOSAL received")
            pass


class Client(Agent):
    def __init__(self, aid, vendeur_aid):
        super(Client, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Je suis le client ')
        self.budget = 1500
        self.vendeur = vendeur_aid
        self.behaviours.append(ClientBehaviour(self))


class ClientBehaviour(Behaviour):

    def on_start(self):
        self.cpt = 0
        self.aleatoire = random.uniform(0.4, 0.7)  # Pourcentage pour lequel le client accepte l'offre
        display_message(self.agent.aid.name, 'Je suis prêt'.format(self.agent.aid.name))

    def generate_proposition(self):
        return int(random.uniform(0, self.agent.budget * self.aleatoire))

    def execute(self, message):
        if message.performative == ACLMessage.CFP:
            reception = int(message.content)
            self.cpt += 1
            if (self.cpt == 1):
                msg = 'Prix initial [' + str(reception) + '] reçu'
            else:
                msg = 'Proposition [' + str(reception) + '] reçue'
            display_message(self.agent.aid.name, msg)
            # Proposition supérieur au budget du client
            if reception > self.agent.budget:
                rejection = ACLMessage(ACLMessage.REJECT_PROPOSAL)
                self.agent.send(rejection)
                msg = 'Proposition [' + str(reception) + '] refusée.'
                display_message(self.agent.aid.name, msg)
                proposition = self.agent.budget  # Nouvelle proposition au budget du client
                proposal = ACLMessage(ACLMessage.PROPOSE)
                proposal.add_receiver(self.agent.vendeur)
                proposal.set_content(str(proposition))
                self.agent.send(proposal)
                msg = 'Proposition [' + str(proposition) + '] envoyée à: {}'.format(self.agent.vendeur)
                display_message(self.agent.aid.name, msg)
            else:
                if reception <= self.agent.budget * self.aleatoire:
                    acceptation = ACLMessage(ACLMessage.ACCEPT_PROPOSAL)
                    self.agent.send(acceptation)
                    msg = 'Proposition [' + str(reception) + '] acceptée de : {}'.format(self.agent.vendeur)
                    display_message(self.agent.aid.name, msg)
                    self.agent.budget = self.agent.budget - reception
                    display_message(self.agent.aid.name, 'Nouveau budget : {}'.format(self.agent.budget))
                    self.agent.behaviours.remove(self)
                else:
                    rejection = ACLMessage(ACLMessage.REJECT_PROPOSAL)
                    self.agent.send(rejection)
                    msg = 'Proposition [' + str(reception) + '] refusée.'
                    display_message(self.agent.aid.name, msg)
                    proposition = self.generate_proposition()
                    proposal = ACLMessage(ACLMessage.PROPOSE)
                    proposal.add_receiver(self.agent.vendeur)
                    proposal.set_content(str(proposition))
                    self.agent.send(proposal)
                    msg = 'Proposition [' + str(proposition) + '] envoyée à: {}'.format(self.agent.vendeur)
                    display_message(self.agent.aid.name, msg)
        if message.performative == ACLMessage.ACCEPT_PROPOSAL:
            self.agent.budget = self.agent.budget - int(message.content)
            display_message(self.agent.aid.name, 'Nouveau budget : {}'.format(self.agent.budget))
            self.agent.behaviours.remove(self)
        if message.performative == ACLMessage.REJECT_PROPOSAL:
            display_message(self.agent.aid.name, "REJECT PROPOSAL received")
            pass


class RandomWalker(Vendeur):
    def __init__(self, aid):
        super(RandomWalker, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Je suis un Random Walker')
        self.call_later(5, self.initialize_send)

    def initialize_send(self):
        randomwalker_behaviour = RandomWalkerBehaviour(self)
        self.behaviours.append(randomwalker_behaviour)
        randomwalker_behaviour.on_start()


class RandomWalkerBehaviour(VendeurBehaviour):
    def generate_proposition(self, precedente_valeur):  # Overriding
        return random.randrange(precedente_valeur, self.agent.prix_initial)


class CarefulAgent(Vendeur):
    def __init__(self, aid):
        super(CarefulAgent, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Je suis un Careful Agent')
        self.call_later(7, self.initialize_send)

    def initialize_send(self):
        carefulagent_behaviour = CarefulAgentBehaviour(self)
        self.behaviours.append(carefulagent_behaviour)
        carefulagent_behaviour.on_start()


class CarefulAgentBehaviour(VendeurBehaviour):
    def generate_proposition(self):  # Overriding
        return int(self.proposition * 0.95)  # Concession de 5%


class ImitatingAgent(Vendeur):
    def __init__(self, aid):
        super(ImitatingAgent, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Je suis un Imitating Agent')
        self.call_later(9, self.initialize_send)

    def initialize_send(self):
        imitatingagent_behaviour = ImitatingAgentBehaviour(self)
        self.behaviours.append(imitatingagent_behaviour)
        imitatingagent_behaviour.on_start()


class ImitatingAgentBehaviour(Behaviour):
    def __init__(self, agent):
        super().__init__(agent)
        self.proposition = self.agent.prix_initial
        self.precedente_valeur = 0

    def generate_proposition(self):
        return max(self.proposition - (self.proposition - self.precedente_valeur), self.agent.prix_reserve)


class AdaptiveAgent(RandomWalker, CarefulAgent, ImitatingAgent):
    def __init__(self, aid):
        super(ImitatingAgent, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Je suis un Adaptive Agent')
        self.call_later(9, self.initialize_send)

    def initialize_send(self):
        adaptiveagent_behaviour = AdaptiveAgentBehaviour(self)
        self.behaviours.append(adaptiveagent_behaviour)
        adaptiveagent_behaviour.on_start()


class AdaptiveAgentBehaviour(RandomWalkerBehaviour, CarefulAgentBehaviour, ImitatingAgentBehaviour):
    def __init__(self, agent):
        super().__init__(agent)
        self.proposition = self.agent.prix_initial
        self.precedente_valeur = 0

    def generate_proposition(self):
        r = random.randint(0, 2)
        if r == 0:
            return RandomWalker.generate_proposition(self)
        elif r == 1:
            return CarefulAgent.generate_proposition(self)
        else:
            return ImitatingAgent.generate_proposition(self)


if __name__ == '__main__':
    agents = []
    port = 2000

    vendeur_agent_name = 'vendeur_{}@localhost:{}'.format(port, port)
    vendeur_agent = RandomWalker(AID(name=vendeur_agent_name))

    client_agent_name = 'client_agent_{}@localhost:{}'.format(port + 2, port + 2)
    client_agent = Client(AID(name=client_agent_name), vendeur_agent_name)
    agents.append(client_agent)

    vendeur_agent.client = client_agent_name
    agents.append(vendeur_agent)

    vendeur_agent_name2 = 'vendeur_{}@localhost:{}'.format(port + 1, port + 1)
    vendeur_agent2 = CarefulAgent(AID(name=vendeur_agent_name2))

    client_agent_name2 = 'client_agent_{}@localhost:{}'.format(port + 3, port + 3)
    client_agent2 = Client(AID(name=client_agent_name2), vendeur_agent_name2)
    agents.append(client_agent2)

    vendeur_agent2.client = client_agent_name2
    agents.append(vendeur_agent2)

    vendeur_agent_name3 = 'vendeur_{}@localhost:{}'.format(port + 4, port + 4)
    vendeur_agent3 = ImitatingAgent(AID(name=vendeur_agent_name3))

    client_agent_name3 = 'client_agent_{}@localhost:{}'.format(port + 5, port + 5)
    client_agent3 = Client(AID(name=client_agent_name3), vendeur_agent_name3)
    agents.append(client_agent3)

    vendeur_agent3.client = client_agent_name3
    agents.append(vendeur_agent3)

    vendeur_agent_name4 = 'vendeur_{}@localhost:{}'.format(port + 6, port + 6)
    vendeur_agent4 = ImitatingAgent(AID(name=vendeur_agent_name4))

    client_agent_name4 = 'client_agent_{}@localhost:{}'.format(port + 7, port + 7)
    client_agent4 = Client(AID(name=client_agent_name4), vendeur_agent_name4)
    agents.append(client_agent4)

    vendeur_agent4.client = client_agent_name4
    agents.append(vendeur_agent4)

    start_loop(agents)
