from Visitor import Visitor
from abc import ABC

from AST import *


from StaticError import *

# parameter type
class ParamType:
    def __init__(self,name,returnType, inherit: bool = False):
        self.name = name
        self.returnType = returnType
        self.inherit = inherit

# luu tru var hoac function, 
# 
# flag de xac dinh var hay function
# flag = 0: var
# flag = 1: function da duoc khai bao
# flag = 2: function chua duoc khai bao, nam trong prototype
class Symbol:
    def __init__(self, name, returnType, flag: int = 0, param = [],  inherit: str = None):
        self.name = name
        self.returnType = returnType
        self.flag = flag
        self.param = param
        self.inherit = inherit
        # self.value = value
        
    
class GetEnv(Visitor):
        # decls: List[Decl]
    def __init__(self, ast):
        self.ast = ast
    def check(self):
        return self.visitProgram(self.ast, [])
    def visitProgram(self, ast, param):
        
        o = param
        for decl in ast.decls:
            o.append(self.visit(decl, o))
            
        return o

        # name: str, typ: Type, init: Expr or None = None
        # param = [Symbol(ast.name, ast.typ, ast.init)] in global
    def visitVarDecl(self, ast, param):
        for var in param:
            if var.name == ast.name:
                # raise Redeclared(Variable(), ast.name)
                pass
        return Symbol(ast.name, ast.typ)
        
    # _____________________________________________________________
    # name: str, return_type: Type, params: List[ParamDecl], inherit: str or None, body: BlockStmt
    # param [Symbol()] in global scope)
    # _____________________________________________________________
    def visitFuncDecl(self, ast, param):
        
        paramList = []
        for i in ast.params:
            paramList.append(self.visit(i, paramList))
        return Symbol(ast.name, ast.return_type, True, paramList, ast.inherit)
    # _________________________________________________________
    # name: str, typ: Type, inherit: str or None
    # param: [ParamDecl()]
    # _________________________________________________________
    def visitParamDecl(self, ast, param):
        for paramDecl in param:
            if paramDecl.name == ast.name:
                # raise Redeclared(Parameter(), ast.name)
                pass
        return ParamType(ast.name, ast.typ, ast.inherit)

# _________________________________________________________
# infer typ for id
# infer string
# _________________________________________________________
def infer(name, typ, param):
    env = param[0]
    prototype = param[1]
    for symbolList in env:
        for sym in symbolList:
            if sym.name == name:
                sym.returnType = typ
                return typ
    # case id is not in env, change in prototype, and add to env
    # symAddEnv = None
    # for sym in prototype:
    #     if sym.name == name:
    #         sym.returnType = typ
            
    #         ret = typ
    
# _________________________________________________________
# infer typ for param_name in func_name
# global_env can be env or prototype
# _________________________________________________________
def inferParam(func_name, param_name , typ, global_env):
    for func in global_env:
        if func.name == func_name:
            for param in func.param:
                if param.name == param_name:
                    param.returnType = typ
                    return typ
        
def intersection(lst1, lst2): 
    lst3 = [value for value in lst1 if value in lst2] 
    return lst3   
    

class StaticChecker(Visitor):
    
    def __init__(self, ast):
        self.ast = ast
    def check(self):
        return self.visitProgram(self.ast, [])
    
        # decls: List[Decl]
    def visitProgram(self, ast, param): 
        # special functions
        env = [[]]
        # special functions
        env[0] = [Symbol("readInteger", IntegerType(), 1),
            Symbol("printInteger", VoidType(), 1, [ParamType("anArg", IntegerType())]),
            Symbol("readFloat", FloatType(), 1),
            Symbol("printFloat", VoidType(), 1, [ParamType("anArg", FloatType())]),
            Symbol("readBoolean", BooleanType(), 1),
            Symbol("printBoolean", VoidType(), 1, [ParamType("anArg", BooleanType())]),
            Symbol("readString", 1, None, StringType()),
            Symbol("printString", VoidType(), 1, [ParamType("anArg", StringType())])
        ]
        
        # first check, get all function and variable of global scope
        globalScopePrototype = GetEnv(ast).visitProgram(ast, [])
        
        # env[0] += globalEnv
        # second check, check all declare
        
        for decl in ast.decls:
            self.visit(decl, [True,env,globalScopePrototype])
        
        # raise NoEntryPoint() in the end of 2nd check
        for func in env[-1]:
            if func.name == "main" and type(func.returnType) == VoidType and func.flag == 1:
                return
        raise NoEntryPoint()
    
    # _____________________________________________________________

    # param of Vardecl can be 2 type
    # type1 : call from program
    # # func/var param # [0] program_call: bool, flag for distinguish visit vardecl from program or 
			            # [1] env,
			            # [2] globalScopePrototype
    # type2 : call from stmt
    # stmt param	# [0] program_call: bool, flag for distinguish visit vardecl from program or 
				# [1] env, 
				# [2] globalScopePrototype
				# [3] is_in_loop: [True], # list flag for check break, continue stmt error must in loop
				# [4] is_function_body: Bool, # only use when funcdclare visit block stmt, if == False, block call from stmt
				# [5] Symbol() of current function, 
				# [6] is_init_for: Bool, # flag for check init stmt of for stmt
				# [7] is_in_if: [True] # list flag
    # _____________________________________________________________
    # name: str, typ: Type, init: Expr or None = None
    # _____________________________________________________________
    def visitVarDecl(self, ast, param):
        env = param[1]
        globalEnvPrototype = param[2]
        # check redelare in current scope (can be local scope or global scope)
        for sym in env[0]:
            if sym.name == ast.name:
                raise Redeclared(Variable(), ast.name)
        if param[0] == True: # in global scope, env = [globalEnv]
            env[0].append(Symbol(ast.name, ast.typ))
            
        # kiem tra tinh hop le cua ve trai
        
        if ast.init is None:
            if type(ast.typ) is AutoType: # declare auto type var but no init
                raise Invalid(Variable(),ast.name)
            return Symbol(ast.name, ast.typ)
        
        elif ast.init is not None:
            
            # if ast.typ is ArrayType:
            exprType = self.visit(ast.init, [env, globalEnvPrototype])
            
            if type(exprType) is AutoType:
                infer(ast.init.name, ast.typ, [env, globalEnvPrototype])
                exprType = self.visit(ast.init, [env, globalEnvPrototype])
            if type(ast.typ) is AutoType:
                return Symbol(ast.name, exprType)
            elif type(ast.typ) is IntegerType and type(exprType) is FloatType:
                raise TypeMismatchInVarDecl(ast)
            elif type(ast.typ) is FloatType and type(exprType) is IntegerType:
                return Symbol(ast.name, ast.typ)
            elif type(ast.typ) is type(exprType) and type(ast.typ) in [IntegerType, FloatType, BooleanType, StringType]:
                return Symbol(ast.name, ast.typ)
            elif type(ast.typ) is not type(exprType) and type(ast.typ) in [IntegerType, FloatType, BooleanType, StringType] and type(exprType) in [IntegerType, FloatType, BooleanType, StringType]: # khong dung type de so sanh truc tiep dimension and type of array
                raise TypeMismatchInVarDecl(ast)
            elif type(ast.typ) is not type(exprType) and type(ast.typ) not in [IntegerType, FloatType, BooleanType, StringType] and type(exprType) in [IntegerType, FloatType, BooleanType, StringType]: # khong dung type de so sanh truc tiep dimension and type of array
                raise TypeMismatchInVarDecl(ast)
            elif type(ast.typ) is not type(exprType) and type(ast.typ) in [IntegerType, FloatType, BooleanType, StringType] and type(exprType) not in [IntegerType, FloatType, BooleanType, StringType]: # khong dung type de so sanh truc tiep dimension and type of array
                raise TypeMismatchInVarDecl(ast)
            else:
                # ca 2 deu la array
                # flatten array
                dimen = 1
                for i in ast.typ.dimensions:
                    dimen *= i
                    
                exprDimen = 1
                for i in exprType.dimensions:
                    exprDimen *= i
                
                if ast.typ.typ != exprType.typ or dimen != exprDimen: 
                    
                    raise TypeMismatchInVarDecl(ast)
                return Symbol(ast.name, ast.typ)
            
            
        
    # _____________________________________________________________
    # name: str, return_type: Type, params: List[ParamDecl], inherit: str or None, body: BlockStmt
    # # func/var param #  [0] program_call: bool, flag for distinguish visit vardecl from program or 
			            # [1] env,
			            # [2] globalScopePrototype
    # _____________________________________________________________
    def visitFuncDecl(self, ast, param):
        env = param[1]
        # global duyet ban dau prototype, 
        # chi dung de check ham cha viet sau ham con, chua dc khai bao
        globalScopePrototype = param[2] 
        
        # them cac ten cua param vao local_scope
        listParam = ast.params 
        localEnv = []
        # check redeclare function
        for sym in env[0]:
            if sym.name == ast.name:
                if(sym.flag == 1):
                    raise Redeclared(Function(), ast.name) # function is already declared
        symInfered = None
        for sym in globalScopePrototype:
            if sym.name == ast.name:
                symInfered = sym
                break
        # infer return type for function, and type of param 
        # ast.return_type = type(symInfered.returnType)
        # visit and check redeclare param
        paramList = []
        for i in ast.params:
            paramList.append(self.visit(i, paramList))
            
        # symbol been infered to scope
        env[0] += [symInfered]
        # add param to local scope, which is inferd
        listParam = symInfered.param
        for i in listParam:
            localEnv += [Symbol(i.name, i.returnType)]
        # create new scope
        env = [[]] + env
        env[0] = localEnv            
           
        # visit block statement
        self.visit(ast.body, [False, env, globalScopePrototype, True, symInfered, [] , False, []])
        # end of scope block statement, remove local scope
        env = env[1:]
        
        
        
    # _________________________________________________________
    # name: str, typ: Type, inherit: str or None
    # param: [ParamDecl()]
    # _________________________________________________________
    def visitParamDecl(self, ast, param):
        for paramDecl in param:
            if paramDecl.name == ast.name:
                raise Redeclared(Parameter(), ast.name)
    
        return Symbol(ast.name, ast.typ)
        

    
    # *********************************************************
    # _______________GROUP VISIT STMT__________________________
    # *********************************************************
    # stmt param	# [0] program_call: bool, flag for distinguish visit vardecl from program or 
				# [1] env, 
				# [2] globalScopePrototype
				# [3] is_function_body_block: Bool, # only use when funcdclare visit block stmt, if == False, block call from stmt
				# [4] Symbol() of current function, 
				# [5] is_in_loop: [True], # list flag for check break, continue stmt error must in loop
				# [6] is_init_for: Bool, # flag for check init stmt of for stmt
				# [7] not_return_in_block: [True] # list flag for return, True is chua return in block
    # rule 1: stmt not used that parameter, pass param[i] in visit next stmt
    # _________________________________________________________
    # BlockStmt body: List[Stmt or VarDecl]
    # _________________________________________________________
    # blockstmt is using by function or other stmt
    # if blockstmt is call from function, env is created in visitFuncDecl (1)
    # if blockstmt is call from other stmt, env is created in here (2)
    #       in case (1): if inherit, parentfunc is Symbol of parent function, 
    #                     has been checked in visitFuncDecl
    # _________________________________________________________
    def visitBlockStmt(self, ast, param):
        env = param[1]
        prototypeEnv = param[2]
        is_func_body = param[3]
        current_func = param[4]
        is_in_loop = param[5]
        is_init_for = param[6]
        not_return_in_block = param[7]
        localEnv = []
        # ____________________
        # case block statement is function body, 
        # be called from visitFuncDecl,     
        # local env has been created in visitFuncDecl
        
        if current_func.inherit is not None:
            # check function name in env, if not found, check in prototype, and infer param and return type
            parentFuncName = current_func.inherit 
            beFound = 0 # 0: not found, 1: found in env, 2: found in prototype
            parent_function = None
            for symbol in env[-1]:
                if symbol.name == parentFuncName:
                    beFound = 1
                    parent_function = symbol
                    break
            
            if beFound == 0:
                for symbol in prototypeEnv:
                    if symbol.name == parentFuncName:
                        beFound = 2
                        parent_function = symbol
                        break
            # parent function is not found
            if beFound == 0:
                raise Undeclared(Function(), parentFuncName)
            # check parent is a function when call super
            if parent_function.flag == 0:
                raise Undeclared(Function(), parentFuncName)
            
            # case call super or preventdefault
            
            if len(ast.body) > 0 and type(ast.body[0]) is CallStmt:
                
                # name: str, args: List[Expr]
                # expr la CallStmt 
                expr = ast.body[0]
                if expr.name == "super":
                    # check parent is a function
                    
                    # visit father function, env[-1] is global scope
                    # get name and type of params of parent function
                    parent_params = parent_function.param
                    if len(expr.args) > len(parent_params):
                        raise TypeMismatchInExpression(expr.args[len(parent_params)]) # raise args du thua dau tien
                    elif len(expr.args) < len(parent_params):
                        raise TypeMismatchInExpression(None)
                    
                    # check type of each param of super function and the parent function
                    for i in range(len(expr.args)):
                        typArgs = self.visit(expr.args[i], [env, prototypeEnv])
                        if type(typArgs) is AutoType and type(parent_function[i].returnType) is AutoType:
                            pass # not error type cannot be inferred
                        elif type(typArgs) is AutoType: # infer the type of param in father function for id in super function
                            infer(expr.args[i].name, parent_params[i].returnType, [env, prototypeEnv])
                            pass 
                        elif type(parent_params[i].returnType) is AutoType: # infer the type of param in super function for father function
                            inferParam(parent_function.name,parent_function.param[i].name, typArgs, env[-1] if beFound == 1 else prototypeEnv)
                        elif type(typArgs) is IntegerType and type(parent_params[i].returnType) is FloatType:
                            # convert the integer type param to float
                            pass
                        elif type(typArgs) is not type(parent_params[i].returnType):
                            raise TypeMismatchInExpression(expr.args[i]) # args dau tien khong khop kieu
                        else: # expr.args[i] is parent_params[i]                            
                            pass
                    # check if the name of params turn out 2 times
                    
                    
                    
                    # check if the name of params inherit in father function is the same as the name of params in function
                    # if not, add the param to the current environment                    
                    for param in parent_params:
                        for symbol in env[0]:
                            if param.name == symbol.name and param.inherit == True:
                                raise Invalid(Parameter(), param.name)
                        if param.inherit == True:
                            env[0] += [Symbol(param.name, param.returnType)]
                        # else: # param.inherit == False
                        
                    
                    
                    
                elif expr.name == "preventDefault":
                    # khong goi super()
                    pass
                else: # firststmt is another callfunc, -> goi ham super() khong tham so
                    if len(parent_params) != 0:
                        raise TypeMismatchInStatement()
                    else: # ham cha khong co tham so nen ko thua huong
                        pass
            
                        
        else: # non inherit case, special func for inherit cannot be called
            
            if len(ast.body) > 0:
                stmt = ast.body[0]
                if type(stmt) is CallStmt and (stmt.name == "preventDefault" or stmt.name == "super"):
                    raise InvalidStatementInFunction(current_func.name)
            pass
        
        # --------------------------------------------------------
        # case block is_block_body, be called from other statement
        # local env create here          
        if is_func_body == False: 
            # create new scope
            env = [[]] + env
            env[0] = localEnv  
        
        # xu ly chung cho ca 2 truong hop funcbody va blockbody
        not_return_in_block.append(True)
        
        
        for stmt in ast.body:
            
            if isinstance(stmt, VarDecl):
                env[0].append(self.visit(stmt, [False, env, prototypeEnv,False, current_func, is_in_loop, is_init_for, not_return_in_block]))
            else: # stmt is Stmt
                self.visit(stmt, [False, env, prototypeEnv,False, current_func, is_in_loop, is_init_for, not_return_in_block])
        # if block is blockbody, local env is removed here
        # if block is function body, local env is removed in visitFuncDecl
        if is_func_body == False: 
            env = env[1:]
        not_return_in_block.pop()
        return 
        # _________________________________________________________
    # lhs: LHS, rhs: Expr
    # stmt param (is_in_loop: Bool, env, False, None, None, is_init_for: Bool)
    # _________________________________________________________
    def visitAssignStmt(self, ast, param):
        env = param[1]
        prototype = param[2]
        is_init_for = param[6]
        rightType = self.visit(ast.rhs, [env, prototype])
        leftType = self.visit(ast.lhs, [env, prototype])

        if is_init_for: 
            if type(leftType) is not IntegerType:
                raise TypeMismatchInStatement(ast)
        if type(leftType) is AutoType:            
            infer(ast.lhs.name, rightType, [env, prototype])
            return 
        elif type(rightType) is AutoType:
            infer(ast.rhs.name, leftType, [env, prototype])
            return 
        elif type(leftType) is IntegerType and type(rightType) is FloatType:
            raise TypeMismatchInStatement(ast)
        elif type(leftType) is FloatType and type(rightType) is IntegerType:
            pass
        elif type(leftType) is not type(rightType):
            raise TypeMismatchInExpression(ast.rhs)
        else: # leftType == rightType
            return
    # _________________________________________________________    
    # cond: Expr, tstmt: Stmt, fstmt: Stmt or None = None
    # _________________________________________________________
    def visitIfStmt(self, ast, param):
        env = param[1]
        prototype = param[2]
        cond = self.visit(ast.cond, [env, prototype])
        not_return_in_block = param[7]
        
        if type(cond) is not BooleanType:
            raise TypeMismatchInStatement(ast) # tiep tuc truyen tham so cho visit stmt
        if type(ast.tstmt) is not BlockStmt:
            not_return_in_block.append(True)
            self.visit(ast.tstmt, [param[0], env, param[2], param[3], param[4], param[5], param[6], not_return_in_block])
            not_return_in_block.pop()
        else:
            self.visit(ast.tstmt, [param[0], env, param[2], param[3], param[4], param[5], param[6], not_return_in_block])
        
        if ast.fstmt is not None:
            if type(ast.fstmt) is not BlockStmt:
                not_return_in_block.append(True)
                self.visit(ast.fstmt, [param[0], env, param[2], param[3], param[4], param[5], param[6], not_return_in_block])
                not_return_in_block.pop()
            else:
                self.visit(ast.fstmt, [param[0], env, param[2], param[3], param[4], param[5], param[6], not_return_in_block])
            
    # _________________________________________________________    
    # init: AssignStmt, cond: Expr, upd: Expr, stmt: Stmt
    # stmt param (is_in_loop: Bool, env)
    # _________________________________________________________  
    def visitForStmt(self, ast, param):
        env = param[1]
        prototype = param[2]
        is_in_loop = param[5]
        not_return_in_block = param[7]
        assignStmt = self.visit(ast.init, [param[0], env, param[2], param[3], param[4], is_in_loop, True, param[7]]) # id for assignStmt duoc chuan bi ti truoc, khong khoi tao luc nay, id nay kieu int
        cond = self.visit(ast.cond, [env, prototype])
        if type(cond) != BooleanType:
            raise TypeMismatchInStatement(ast)
        upd = self.visit(ast.upd, [env, prototype])
        if type(upd) != IntegerType:
            raise TypeMismatchInStatement(ast)

        env = [[]] + env
        is_in_loop.append(True)
        if type(ast.stmt) is not BlockStmt:
            not_return_in_block.append(True)
            self.visit(ast.stmt, [param[0], env, param[2], param[3], param[4], param[5], param[6], not_return_in_block])
            not_return_in_block.pop()
        else:
            self.visit(ast.stmt, [param[0], env, param[2], param[3], param[4], param[5], param[6], not_return_in_block])
        env = env[1:]
        is_in_loop.pop()
    
    # _________________________________________________________    
    # cond: Expr, stmt: Stmt
    # stmt param (is_in_loop: Bool, env)
    # _________________________________________________________
    def visitWhileStmt(self, ast, param): 
        env = param[1]
        prototype = param[2]
        is_in_loop = param[5]
        not_return_in_block = param[7]
        cond = self.visit(ast.cond, [env, prototype])
        if type(cond) != BooleanType:
            raise TypeMismatchInStatement(ast)
        
        env = [[]] + env
        is_in_loop.append(True)
        if type(ast.stmt) is not BlockStmt:
            not_return_in_block.append(True)
            self.visit(ast.stmt, [param[0], env, param[2], param[3], param[4], param[5], param[6], not_return_in_block])
            not_return_in_block.pop()
        else:
            self.visit(ast.stmt, [param[0], env, param[2], param[3], param[4], param[5], param[6], not_return_in_block])
        env = env[1:]
        is_in_loop.pop()
        
    # _________________________________________________________    
    # cond: Expr, stmt: BlockStmt
    # stmt param (is_in_loop: Bool, env)
    # _________________________________________________________
    def visitDoWhileStmt(self, ast, param): 
        env = param[1]
        prototype = param[2]
        is_in_loop = param[5]
        not_return_in_block = param[7]
        
        env = [[]] + env
        is_in_loop.append(True)
        # dowhile stmt must be block stmt
        if type(ast.stmt) is not BlockStmt:
            not_return_in_block.append(True)
            self.visit(ast.stmt, [param[0], env, param[2], param[3], param[4], param[5], param[6], not_return_in_block])
            not_return_in_block.pop()
        else:
            self.visit(ast.stmt, [param[0], env, param[2], param[3], param[4], param[5], param[6], not_return_in_block])
        cond = self.visit(ast.cond, [env, prototype])
        if type(cond) != BooleanType:
            raise TypeMismatchInStatement(ast)
        
        env = env[1:]
        is_in_loop.pop()
    
    # _________________________________________________________    
    # stmt param (is_in_loop: Bool, env)
    # _________________________________________________________
    def visitBreakStmt(self, ast, param):
        env = param[1]
        is_in_loop = param[5]
        if len(is_in_loop) == 0:
            raise MustInLoop(ast)
        elif is_in_loop[-1] == True: # case first break in loop
            is_in_loop[-1] = False
            return
        else: # case second break
            return 
            
    # _________________________________________________________    
    # stmt param (is_in_loop: Bool, env)
    # _________________________________________________________
    def visitContinueStmt(self, ast, param): 
        env = param[1]
        is_in_loop = param[5]
        if len(is_in_loop) == 0:
            raise MustInLoop(ast)
        else:
            return 
    
    # _________________________________________________________
    # Rerturnstmt expr: Expr or None = None
    # # stmt param (is_in_loop: Bool, env, is_function_body: Bool, 
    # Symbol() of current function,
    # Symbol() of parent function)
    # _________________________________________________________
    def visitReturnStmt(self, ast, param):
        env = param[1]
        prototype = param[2] 
        currentFunc = param[4]
        is_in_loop = param[5]
        not_return_in_block = param[7]
        if(len(not_return_in_block) == 0):
            pass # never happen
        
        if not_return_in_block[-1] == False: # case second return
            return # another return in block will be ignored
        not_return_in_block[-1] = False # case first return
        
        return_type = None
        
        if ast.expr is None: # dung == la error luon
            return_type = VoidType()
        else :
            return_type = self.visit(ast.expr, [env, prototype])
        
        for sym in env[-1]:
            if sym.name == currentFunc.name:
                currentFunc = sym
        if type(currentFunc.returnType) is AutoType:
            for sym in env[-1]:
                if sym.name == currentFunc.name:
                    sym.returnType = return_type
        if type(currentFunc.returnType) is type(return_type):
            return
        else:
            raise TypeMismatchInStatement(ast)
        
    # _________________________________________________________
    # CallStmt(Stmt)
    # name: str, args: List[Expr]
    # stmt param (is_in_loop: Bool, env 
    # _________________________________________________________
    def visitCallStmt(self, ast, param):
        env = param[1]
        prototype = param[2]
        if ast.name == "super" or ast.name == "preventDefault":
            if (ast.name == "preventDefault" and len(ast.args) != 0):
                raise TypeMismatchInExpression(ast.args[0])
            return
        # check function name in local
        for localEnv in env[:-1]:
            for symbol in localEnv: # find id in the current environment
                if ast.name == symbol.name:
                    raise TypeMismatchInStatement(ast) # id is declared in current scope but is not a function
        # check function name in env, if not found, check in prototype, and infer param and return type
        beFound = 0 # 0: not found, 1: found in env, 2: found in prototype
        funcSym = None
        for symbol in env[-1]:
            if symbol.name == ast.name:
                beFound = 1
                funcSym = symbol
                break
        
        if beFound == 0:
            for symbol in prototype:
                if symbol.name == ast.name:
                    beFound = 2
                    funcSym = symbol
                    break
        if beFound == 0:
            raise Undeclared(Function(), ast.name)
            

        if funcSym.flag == 0: # is a var
            raise TypeMismatchInStatement(ast) 
        if len(ast.args) > len(funcSym.param):
            raise TypeMismatchInStatement(ast)
        elif len(ast.args) < len(funcSym.param):
            raise TypeMismatchInStatement(ast)
        for i in range(len(ast.args)):
            arg = self.visit(ast.args[i], [env, prototype])
            if type(funcSym.param[i].returnType) is AutoType:
                inferParam(funcSym.name,funcSym.param[i].name, arg, env[-1] if beFound == 1 else prototype)
            elif type(arg) is IntegerType and type(funcSym.param[i].returnType) is FloatType:
                # convert the param to float
                # raise TypeMismatchInStatement(ast) # cho phep chuyen kieu
                pass
            elif type(arg) is not type(funcSym.param[i].returnType):
                
                raise TypeMismatchInStatement(ast)
        if (beFound == 2): # call func chua duoc declare, declare 
            funcSym.flag = 2 # declare from prototype
            env[-1].append(funcSym)
        return # stmt chi check loi, khong tra ve kieu
        
    # ************************************************************
    #  GROUP VISIT EXPRESSION
    # Param: env, prototype
    # _________________________________________________________
    # FuncCall(Expr)
    # name: str, args: List[Expr]
    # _________________________________________________________
    def visitFuncCall(self, ast, param):
        env = param[0]
        prototype = param[1]
        if ast.name == "super" or ast.name == "preventDefault":
            return # khong co testcase nay
        # check function name in local
        for localEnv in env[:-1]:
            for symbol in localEnv: # find id in the current environment
                if ast.name == symbol.name:
                    raise TypeMismatchInExpression(ast) # id is declared in current scope but is not a function
                
        # check function name in env, if not found, check in prototype, and infer param and return type
        beFound = 0 # 0: not found, 1: found in env, 2: found in prototype
        funcSym = None
        for symbol in env[-1]:
            if symbol.name == ast.name:
                beFound = 1
                funcSym = symbol
                break
        
        if beFound == 0:
            for symbol in prototype:
                if symbol.name == ast.name:
                    beFound = 2
                    funcSym = symbol
                    break
        if beFound == 0:
            raise Undeclared(Function(), ast.name)
            

        if funcSym.flag == 0: # is a var
            raise TypeMismatchInExpression(ast)
        if (type(funcSym.returnType) == VoidType):
            raise TypeMismatchInExpression(ast)
        if len(ast.args) > len(funcSym.param):
            raise TypeMismatchInExpression(ast.args[len(funcSym.param)])
        elif len(ast.args) < len(funcSym.param):
            raise TypeMismatchInExpression(None)
        for i in range(len(ast.args)):
            arg = self.visit(ast.args[i], [env, prototype])
            if type(funcSym.param[i].returnType) is AutoType:
                inferParam(funcSym.name,funcSym.param[i].name, arg, env[-1] if beFound == 1 else prototype)
            elif type(arg) is IntegerType and type(funcSym.param[i].returnType) is FloatType:
                # convert the param to float
                # raise TypeMismatchInExpression(ast) # cho phep convert
                pass
            elif type(arg) is not type(funcSym.param[i].returnType):
                
                raise TypeMismatchInExpression(ast)
        if (beFound == 2): # call func chua duoc declare, declare 
            funcSym.flag = 2 # declare from prototype
            env[-1].append(funcSym)
        return symbol.returnType # expr tra ve kieu
        
        
    
    # _________________________________________________________
    # op: str, left: Expr, right: Expr
    # op is Multi: *, /, %
    #        Add: +, -
    #        Logical: &&, ||
    #        Relational: <, >, <=, >=, ==, !=
    #        String: ::
    # _________________________________________________________
    def visitBinExpr(self, ast, param): 
        op = ast.op
        
        leftType = self.visit(ast.left, param)
        rightType = self.visit(ast.right, param)
        if op in ['+', '-', '*', '/']: # operand type is int/float
            if intersection([type(leftType), type(rightType)], [BooleanType(), StringType(), VoidType()]):
                raise TypeMismatchInExpression(ast)
            elif type(leftType) is AutoType and type(rightType) is AutoType:
                return FloatType() # testcase khong co 2 cai auto ko suy dien dc, tra ve float tang ti le dung
            elif type(leftType) is AutoType:
                infer(ast.left.name, rightType, param)
                return rightType
            elif type(rightType) is AutoType:
                infer(ast.right.name, leftType, param)
                return leftType
            elif type(leftType) is IntegerType and type(rightType) is IntegerType:
                return IntegerType()
            elif type(leftType) is FloatType and type(rightType) is FloatType or type(leftType) is IntegerType and type(rightType) is FloatType or type(leftType) is FloatType and type(rightType) is IntegerType:
                return FloatType()
            else: # arrayType
                raise TypeMismatchInExpression(ast)
            
        elif op in ['%']: # operand type is int
            if intersection([type(leftType), type(rightType)], [BooleanType(), StringType(), VoidType(), FloatType()]):
                raise TypeMismatchInExpression(ast)
            elif type(leftType) is AutoType and type(rightType) is AutoType:
                infer(ast.left.name, IntegerType, param)
                infer(ast.right.name, IntegerType, param)
                return IntegerType()
            elif type(leftType) is AutoType:
                infer(ast.left.name, rightType, param)
                return IntegerType()
            elif type(rightType) is AutoType:
                infer(ast.right.name, leftType, param)
                return IntegerType()
            elif type(leftType) is IntegerType and type(rightType) is IntegerType:
                return IntegerType()
            else : # arrayType
                raise TypeMismatchInExpression(ast)
            
        elif op in ['&&', '||']: # operand type is bool
            if intersection([type(leftType), type(rightType)], [IntegerType(), StringType(), VoidType(), FloatType()]):
                raise TypeMismatchInExpression(ast)
            if type(leftType) is AutoType and type(rightType) is AutoType:
                infer(ast.left.name, BooleanType, param)
                infer(ast.right.name, BooleanType, param)
                return BooleanType()
            elif type(leftType) is AutoType:
                infer(ast.left.name, rightType, param)
                return BooleanType()
            elif type(rightType) is AutoType:
                infer(ast.right.name, leftType, param)
                return BooleanType()
            elif type(leftType) is BooleanType and type(rightType) is BooleanType:
                return BooleanType()
            else : # arrayType xuat hien
                raise TypeMismatchInExpression(ast)
        elif op in ['<', '>', '<=', '>=', '==', '!=']: # operand type is int/float, return booltype    
            if intersection([type(leftType), type(rightType)], [BooleanType(), StringType(), VoidType()]):
                raise TypeMismatchInExpression(ast)
            elif type(leftType) is AutoType and type(rightType) is AutoType:
                infer(ast.left.name, BooleanType, param)
                infer(ast.right.name, BooleanType, param)
                return BooleanType() # ti le dung cao hon
            elif type(leftType) is AutoType:
                infer(ast.left.name, rightType, param)
                return BooleanType()
            elif type(rightType) is AutoType:
                infer(ast.right.name, leftType, param)
                return BooleanType()
            elif type(leftType) is IntegerType and type(rightType) is IntegerType:
                return BooleanType()
            elif type(leftType) is FloatType and type(rightType) is FloatType or type(leftType) is IntegerType and type(rightType) is FloatType or type(leftType) is FloatType and type(rightType) is IntegerType:
                return BooleanType()
            else :
                raise TypeMismatchInExpression(ast)
            
            
        elif op in ['::']: # operand type is string, returntype is tring
            if intersection([type(leftType), type(rightType)], [BooleanType(), IntegerType(), VoidType(), FloatType()]):
                raise TypeMismatchInExpression(ast)
            elif type(leftType) is AutoType and type(rightType) is AutoType:
                infer(ast.left.name, StringType, param)
                infer(ast.right.name, StringType, param)
                return StringType()
            elif type(leftType) is AutoType:
                infer(ast.left.name, rightType, param)
                return StringType()
            elif type(rightType) is AutoType:
                infer(ast.right.name, leftType, param)
                return StringType()
            elif type(leftType) is StringType and type(rightType) is StringType:
                return StringType()
            else : # arrayType xuat hien
                raise TypeMismatchInExpression(ast)
    # _________________________________________________________
    # op: str, body: Expr
    # op is Unary: !, -
    # _________________________________________________________
    def visitUnExpr(self, ast, param): 
        op = ast.op
        bodyType = self.visit(ast.body, param)
        if op in ['!']: # operand type is bool
            if type(bodyType) is AutoType:
                infer(ast.body, BooleanType, param)
                return BooleanType()
            elif type(bodyType) is BooleanType:
                return BooleanType()
            else:
                raise TypeMismatchInExpression(ast)
        elif op in ['-']: # operand type is int/float
            if type(bodyType) is AutoType:
                infer(ast.body, IntegerType, param)
                return IntegerType()
            elif type(bodyType) is IntegerType:
                return IntegerType()
            elif type(bodyType) is FloatType:
                return FloatType()
            else:
                raise TypeMismatchInExpression(ast)
    
    
    def visitId(self, ast, param):
        env = param[0]
        prototype = param[1]
        for e in env:
            for sym in e:
                if ast.name == sym.name:
                    return sym.returnType
        raise Undeclared(Identifier(), ast.name)

    

    def visitIntegerType(self, ast, param): return IntegerType()
    def visitFloatType(self, ast, param): return FloatType()
    def visitBooleanType(self, ast, param): return BooleanType()
    def visitStringType(self, ast, param): return StringType()
    
    def visitAutoType(self, ast, param): return AutoType()
    def visitVoidType(self, ast, param): return VoidType()
    
    # (self, dimensions: List[int], typ: AtomicType):
    def visitArrayType(self, ast, param): 
        return ArrayType(ast.dimensions, ast.typ) 
    
    # name: str, cell: List[Expr]
    def visitArrayCell(self, ast, param):
        # thu tu check tu ngoai vao trong, check id, check length, check type exp
        env = param[0]
        # find array in env
        arr = None
        for i in env:
            for sym in i:
                if ast.name == sym.name:
                    arr = sym.returnType
        if arr is None:
            raise Undeclared(Identifier(), ast.name)
        # check cell
        if arr not in [IntegerType(), FloatType(), BooleanType(), StringType(), VoidType(), AutoType()]:
            # check length
            if len(ast.cell) > len(arr.dimensions):                
                # raise TypeMismatchInExpression(ast.cell[len(arr.dimensions)]) # exp du thua dau tien
                raise TypeMismatchInExpression(ast)
            elif len(ast.cell) < len(arr.dimensions): # cho phep truy xuat voi so chieu it hon, lay array con
                if len(ast.cell) == 1 and len(arr.dimensions) == 2:
                    return ArrayType([arr.dimensions[1]], arr.typ)
                elif len(ast.cell) == 1 and len(arr.dimensions) == 3:
                    return ArrayType([arr.dimensions[1], arr.dimensions[2]], arr.typ)
                elif len(ast.cell) == 2 and len(arr.dimensions) == 3:
                    return ArrayType([arr.dimensions[2]], arr.typ)
                # raise TypeMismatchInExpression(ast) # voi dau vao rong, tuong tu giai thich super
            # check type
            for i in range(len(ast.cell)):
                typCell = self.visit(ast.cell[i], param)
                
                if type(typCell) is not IntegerType:
                    raise TypeMismatchInExpression(ast.cell[i])
            return arr.typ
        else: # id khong phai la array
            raise TypeMismatchInExpression(ast)
        
    
    # explist: List[Expr]
    def visitArrayLit(self, ast, param):
        elements = []
        for ele in ast.explist:
            elements += [self.visit(ele, param)]
            
        
        typEle = self.visit(ast.explist[0], param)
        
        for ele in elements:
            if type(ele) != type(typEle):
                raise IllegalArrayLiteral(ast)
        
        if len(elements) >= 2:
            for i in range (1, len(elements)):
                if elements[i] != elements[i-1]:                    
                    raise TypeMismatchInExpression(ast.explist[i])
            
            
        if type(typEle) == ArrayType: # flatten array
            dimen = 1
            for i in typEle.dimensions:
                dimen *= i
            
            return ArrayType([len(ast.explist), dimen], typEle.typ)
        return ArrayType([len(ast.explist)], typEle)
    
    def visitIntegerLit(self, ast, param): return IntegerType()
    def visitFloatLit(self, ast, param): return FloatType()
    def visitStringLit(self, ast, param): return StringType()
    def visitBooleanLit(self, ast, param): return BooleanType()
    