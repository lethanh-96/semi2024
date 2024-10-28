from .non_markovian_thompson_sampling import NonMarkovianThompsonSamplingReceiver
from .delayed_thompson_sampling import DelayedThompsonSamplingReceiver
from .thompson_sampling import ThompsonSamplingReceiver
from .delayed_qlearning import DelayedQLearningReceiver
from .finite_different import FiniteDifferentReceiver
from .qlearning import QLearningReceiver
from .periodic import PeriodicReceiver
from .zooming import ZoomingReceiver
from .greedy import GreedyReceiver
from .debug import DebugReceiver
from .vhct import VhctReceiver

def create_receiver(args):
    if args.receiver == 'greedy':
        return GreedyReceiver(args)
    elif args.receiver == 'periodic':
        return PeriodicReceiver(args)
    elif args.receiver == 'finite_different':
        return FiniteDifferentReceiver(args)
    elif args.receiver == 'qlearning':
        return QLearningReceiver(args)
    elif args.receiver == 'thompson_sampling':
        return ThompsonSamplingReceiver(args)
    elif args.receiver == 'zooming':
        return ZoomingReceiver(args)
    elif args.receiver in ['vhct', 'xab']:
        return VhctReceiver(args)
    elif args.receiver == 'debug':
        return DebugReceiver(args)
    elif args.receiver == 'delayed_qlearning':
        return DelayedQLearningReceiver(args)
    elif args.receiver == 'delayed_thompson_sampling':
        return DelayedThompsonSamplingReceiver(args)
    elif args.receiver == 'non_markovian_thompson_sampling':
        return NonMarkovianThompsonSamplingReceiver(args)
    else:
        raise NotImplementedError
