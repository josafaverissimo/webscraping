import abc


class Boilerplate():
    def __init__(self, inputs):
        self.__inputs = inputs
        self.__user_input = {user_input: None for user_input in inputs}

    def __ask_user_inputs(self):
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

    @abc.abstractclassmethod
    def main(self, user_inputs):
        pass

    def get_user_inputs(self):
        return self.__user_input

    def screen(self):
        stop = 'n'
        flag = 'y'

        while flag != stop:
            self.__ask_user_inputs()

            self.main(self.get_user_inputs())

            flag = input(f'get more data? [{flag}/{stop}]: ')
