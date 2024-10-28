import robot

def receive(args):
    r = robot.create_receiver(args)
    r.run()
