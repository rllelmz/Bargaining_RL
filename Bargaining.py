import random
from pade.acl import aid
from pade.misc.utility import display_message, start_loop
from pade.core.agent import Agent
from pade.behaviours.protocols import Behaviour
from pade.acl.messages import ACLMessage
from pade.acl.aid import AID


class Client(Agent):
    def __init__(self, aid, vendeur_aid):
        super(Client, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Je suis le client ')
        self.budget = 1500
        self.vendeur = vendeur_aid
        self.behaviours.append(ClientBehaviour(self))


class ClientBehaviour(Behaviour):

    def __init__(self, agent):
        super().__init__(agent)
        self.aleatoire = random.uniform(0.4, 0.7)  # Pourcentage pour lequel le client accepte l'offre
        self.cpt = 0

    def on_start(self):
        display_message(self.agent.aid.name, 'Mon comportement est prêt'.format(self.agent.aid.name))

    def generate_proposition(self):
        return int(random.uniform(0, self.agent.budget * self.aleatoire))

    def execute(self, message):
        if message.performative == ACLMessage.CFP:
            reception = int(message.content)
            self.cpt += 1
            if self.cpt == 1:
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
                    nouvelle_proposition = self.generate_proposition()
                    proposition2 = ACLMessage(ACLMessage.PROPOSE)
                    proposition2.add_receiver(self.agent.vendeur)
                    proposition2.set_content(str(nouvelle_proposition))
                    self.agent.send(proposition2)
                    msg = 'Proposition [' + str(nouvelle_proposition) + '] envoyée à: {}'.format(self.agent.vendeur)
                    display_message(self.agent.aid.name, msg)
        if message.performative == ACLMessage.ACCEPT_PROPOSAL:
            self.agent.budget = self.agent.budget - int(message.content)
            display_message(self.agent.aid.name, 'Nouveau budget : {}'.format(self.agent.budget))
            self.agent.behaviours.remove(self)
        if message.performative == ACLMessage.REJECT_PROPOSAL:
            display_message(self.agent.aid.name, "REJECT PROPOSAL received")
            pass


class RandomWalker(Agent):
    def __init__(self, aid):
        super(RandomWalker, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Je suis le Random Walker')
        self.prix_initial = random.randrange(200, 1600)
        self.prix_reserve = int(self.prix_initial * 0.5)
        self.client = "null"
        self.call_later(8, self.initialize_send)

    def initialize_send(self):
        randomwalker_behaviour = RandomWalkerBehaviour(self)
        self.behaviours.append(randomwalker_behaviour)
        randomwalker_behaviour.on_start()


class RandomWalkerBehaviour(Behaviour):
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


class CarefulAgent(Agent):
    def __init__(self, aid):
        super(CarefulAgent, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Je suis le Careful Agent')
        self.prix_initial = random.randrange(200, 1600)
        self.prix_reserve = int(self.prix_initial * 0.25)
        self.client = "null"
        self.call_later(8, self.initialize_send)

    def initialize_send(self):
        carefulagent_behaviour = CarefulAgentBehaviour(self)
        self.behaviours.append(carefulagent_behaviour)
        carefulagent_behaviour.on_start()


class CarefulAgentBehaviour(Behaviour):
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

    def generate_proposition(self):
        return int(self.proposition * 0.95)  # Concession de 5%

    def execute(self, message):
        if message.performative == ACLMessage.PROPOSE:
            msg = 'J\'ai reçu la proposition [' + message.content + '] de : {}'.format(message.sender.name)
            display_message(self.agent.aid.name, msg)
            precedente_valeur = int(message.content)
            self.proposition = self.generate_proposition()
            if precedente_valeur < self.agent.prix_reserve | precedente_valeur < self.proposition:
                # Envoyer un refus
                rejection = ACLMessage(ACLMessage.REJECT_PROPOSAL)
                self.agent.send(rejection)
                msg = 'Proposition [' + str(precedente_valeur) + '] refusée.'
                display_message(self.agent.aid.name, msg)
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


class ImitatingAgent(Agent):
    def __init__(self, aid):
        super(ImitatingAgent, self).__init__(aid=aid)
        display_message(self.aid.localname, 'Je suis l\'Imitating Agent')
        self.prix_initial = random.randrange(1400, 1700)
        self.prix_reserve = int(self.prix_initial * 0.3)
        self.client = "null"
        self.call_later(8, self.initialize_send)

    def initialize_send(self):
        imitatingagent_behaviour = ImitatingAgentBehaviour(self)
        self.behaviours.append(imitatingagent_behaviour)
        imitatingagent_behaviour.on_start()


class ImitatingAgentBehaviour(Behaviour):
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
        return max(self.proposition - (self.proposition - precedente_valeur), self.agent.prix_reserve)

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
                proposal = ACLMessage(ACLMessage.CFP)
                proposal.add_receiver(self.agent.client)
                self.proposition = self.generate_proposition(precedente_valeur)
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

    start_loop(agents)
