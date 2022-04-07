import pulp

class PulpSolve():
    
    def __init__(self,solverName='CBC',solverTime=300,isMsg=0, minGap=1):
        self.solverName = solverName
        self.solverTime = solverTime
        self.isMsg = isMsg
        self.minGap = minGap
    def solver(self, objective, constraints):
        prob = pulp.LpProblem('LP', pulp.LpMinimize)
        prob += objective
        for cons in constraints:
            prob += cons
        # 选择求解器
        if self.solverName in ['CBC','cbc']:
            status = prob.solve(pulp.PULP_CBC_CMD(msg=self.isMsg, maxSeconds=self.solverTime))
        elif self.solverName in ['GUROBI','gurobi']:
            status = prob.solve(pulp.GUROBI_CMD(keepFiles=0, mip=1, msg=self.isMsg, options=[("MIPGap", str(self.minGap))]))
        else:
            status = 0
        #返回求解结果
        if status != 1:
            return None
        else:
            return [(v.name, v.varValue) for v in prob.variables()]  

