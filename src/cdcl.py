class CDCL:
    def __init__(self, variable_num, clause_num, clauses):
        self.variable_num = variable_num
        self.clause_num = clause_num
        self.clauses = clauses

    # check sat with early return
    def check_sat(self, model):
        for clause in self.clauses:
            count = 0
            for literal in clause:
                index = literal - 1 if literal > 0 else literal + 1
                if literal > 0 and model[index] == True:
                    count += 1
                elif literal < 0 and model[index] == False:
                    count += 1
            if count == 0:
                return False
        return True

    # check conflict with early return
    def check_conflict(self, model):
        for clause in self.clauses:
            count = 0
            for literal in clause:
                index = literal - 1 if literal > 0 else literal + 1
                if literal > 0 and model[index] == False:
                    count += 1
                elif literal < 0 and model[index] == True:
                    count += 1
            if count == len(clause):
                return True
        return False

    # naive variable selection
    def choose(self, model):
        for i, _ in enumerate(model):
            if model[i] == None:
                return i
        return None

    def assign(self, model, variable, truth_value):
        copy = model.copy()
        copy[variable] = truth_value
        return copy

    def solve(self):
        def solve_rec(model):
            return None

            if self.check_sat(model):
                return model

            if self.check_conflict(model):
                return None

            variable = self.choose(model)
            print("chosen variable: ", variable)

            try_true = solve_rec(self.assign(model, variable, True))
            if try_true:
                return try_true
            else:
                return solve_rec(self.assign(model, variable, False))

        model = [None for _ in range(self.variable_num)]
        return solve_rec(model)
