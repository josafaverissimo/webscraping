class Boilerplate():
    def __init__(self, inputs, main):
        self.__inputs = inputs
        self.__main = main
        self.__user_input = {user_input: None for user_input in inputs}

    def ask_user_input(self):
        for user_input, handler in self.__inputs.items():
            is_valid = False
            user_entry = None
            
            while is_valid is False:
                if handler['validation'] is not None:
                    user_entry = input(f"{handler['message']}: ")
                    is_valid = handler['validation'](user_entry)
                else:
                    user_entry = input(f"{handler['message']}: ")
                    is_valid = True

            self.__user_input[user_input] = handler['datatype'](user_entry)

    def get_user_inputs(self):
        return self.__user_input

    def screen(self):
        stop = 'n'
        flag = 'y'

        while flag != stop:
            self.ask_user_input()

            self.__main()

            flag = input(f'get more data? [{flag}/{stop}]: ')
