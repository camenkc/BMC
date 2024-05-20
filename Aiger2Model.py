
import os

# for test
file_path = "./aiger-safety-properties/trivial/shift-10101010.aag"
def parse_aiger(lines):
    inputs = []
    outputs = []
    latches = []
    and_gates = []

    input_recorded_num = 0
    latch_recorded_num = 0
    output_recorded_num = 0
    and_recorded_num = 0
    for line in lines:
        line = line.strip()
        # 解析输入
        if line.startswith('aag'):
            _, _, num_inputs, num_latches, num_outputs, and_num = line.split(' ')
            num_inputs = int(num_inputs)
            num_latches = int(num_latches)
            num_outputs = int(num_outputs)
            and_num = int(and_num)
            if num_latches != 0: raise Exception('Aiger file should not have latches')
            continue

        if line.startswith('c'):
            # 注释行，跳过
            break
    
        if input_recorded_num < num_inputs:
            if input_recorded_num==0: print('inputs:')
            print(line)
            input_name = line.strip()
            inputs.append([input_name])
            input_recorded_num += 1
            
        elif latch_recorded_num < num_latches:
            if latch_recorded_num==0: print('latches:')
            print(line)
            latch_a, latch_b = line.strip().split()
            latches.append([latch_a, latch_b])
            latch_recorded_num += 1

        elif output_recorded_num < num_outputs:
            if output_recorded_num==0: print('outputs:')
            print(line)
            output_name = line.strip()
            outputs.append([output_name])
            output_recorded_num += 1
            
        else:# AND门
            if and_recorded_num < and_num:
                if and_recorded_num==0: print('and_gates:')
                print(line)
                tokens = line.split()
                if len(tokens) == 3:
                    a,b,c = tokens
                    and_gates.append((a, [b, c]))
                and_recorded_num += 1
            else: 
                print("Over")
                break
    return num_inputs, num_latches, inputs, outputs, latches, and_gates


def aiger_to_cnf(num_inputs, num_latches, inputs, outputs, latches, and_gates):
    cnf_clauses = []
    # how?
    # for latch_a, latch_b in latches:
    #     # 转换 latch 变量的值和否定值为整数
    #     latch_var = int(latch_a)  # 当前周期的值
    #     latch_next_var = int(latch_b)  # 下一个周期的值

    #     # 处理 latch_next_var 的否定情况
    #     if latch_next_var % 2 == 1:  # 如果是奇数，表示否定
    #         latch_next_var = -(latch_next_var // 2)
    #     else:  # 如果是偶数，表示正常值
    #         latch_next_var = latch_next_var // 2

    #     if latch_var % 2 == 1:  # 如果是奇数，表示否定
    #         latch_var = -(latch_var // 2)
    #     else:  # 如果是偶数，表示正常值
    #         latch_var = latch_var // 2

    #     cnf_clauses.append([-latch_var, latch_next_var])




    for output in outputs:
        output_var = int(output[0])
        if output_var % 2 == 1:
            output_var = -(output_var // 2)
        else: output_var = output_var // 2
        cnf_clauses.append([output_var])




    for a, (b, c) in and_gates:
        a = int(a)
        b = int(b)
        c = int(c)
        # 处理 b 和 c 的否定情况
        if b % 2 == 1:
            b_var = -(b // 2 )
        else:
            b_var = b // 2

        if c % 2 == 1:
            c_var = -(c // 2)
        else:
            c_var = c// 2

        if a % 2 == 1:
            a_var = -(a // 2)
        else:
            a_var = a// 2

        # 添加 CNF 子句
        # ¬a ∨ b
        cnf_clauses.append([-a_var, b_var])
        # ¬a ∨ c
        cnf_clauses.append([-a_var, c_var])
        # ¬b ∨ ¬c ∨ a
        cnf_clauses.append([-b_var, -c_var, a_var])




    return cnf_clauses


def cnf_to_string(cnf_clauses):
    cnf_string = f"p cnf {len(cnf_clauses)}\n"
    for clause in cnf_clauses:
        cnf_string += " ".join(map(str, clause)) + "\n"
    return cnf_string

def write_cnf_file(cnf_string, file_path):
    # 获取文件夹路径
    folder_path = os.path.dirname(file_path)
    # 确保文件夹存在
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    # 写入文件
    with open(file_path, 'w') as f:
        f.write(cnf_string)

def solve_sat(cnf_clauses):
    from pysat.solvers import Minisat22
    
    with Minisat22() as solver:
        for clause in cnf_clauses:
            solver.add_clause(clause)
        return solver.solve()

if __name__ == "__main__":
    with open(file_path, 'r') as file:
        lines = file.readlines()
    num_inputs, num_latches, inputs, outputs, latches, and_gates = parse_aiger(lines)
    cnf_clauses = aiger_to_cnf(num_inputs, num_latches, inputs, outputs, latches, and_gates)
    cnf_string = cnf_to_string(cnf_clauses)
    print(cnf_string)
    print(file_path)
    write_cnf_file(cnf_string,f"cnf_files/{file_path.split('/')[-1].split('.')[0]}.cnf")
    print(solve_sat(cnf_clauses))

    

