import math
import numpy as np
import random
import sys

def placement(cargos, order, box_size):
	x, y, z = 0, 0, 0
	xb, yb, zb = 0, 0, 0
	X, Y, Z = box_size
	vb = X * Y * Z
	vc = 0
	ret = []
	for i in order:
		xc, yc, zc = cargos[i]
		if zc + z > Z or yc > Y or xc > X:
			continue
		if yc + y < Y:
			if xc + x < X:
				ret.append(((x, y, z), tuple(cargos[i])))
				vc += xc * yc * zc
				x += xc
				yb = y + yc if y + yc > yb else yb
				zb = z + zc if z + zc > zb else zb
			else:
				x, y = 0, yb
		else:
			x, y, z = 0, 0, zb
			xb, yb = 0, 0

	return ret, vc/vb

lambda_ = 0.5 # 常数

T_begin = 100 # 初始温度
T_end = 2 # 终止温度
repeat = 100 # 模拟退火算法中重复次数
cool = 0.99 # 冷却因子

pop = 50 # 种群大小
iter_max = 1000 # 最大迭代次数
pm = 0.1 # 变异概率

cargo_data = np.genfromtxt('./cargo', delimiter = '\t', dtype = int)
box_size = (305,121,88) # 箱子尺寸

cargo_count = sum([c[1] for c in cargo_data])
cargos = np.zeros((cargo_count, 3), dtype = int)

k = 0
for i in range(len(cargo_data)):
	for j in range(cargo_data[i][1]):
		cargos[k][:3] = sorted(cargo_data[i][2:5], reverse=True)
		k += 1

# 遗传算法
print('遗传算法......')
def pm_crossover(A, B):
	l = len(A)
	r1, r2 = random.randint(0, l-1), random.randint(0, l-1)
	r1, r2 = min(r1, r2), max(r1, r2)
	A_cross, B_cross = A[r1:r2+1], B[r1:r2+1]
	B2A, A2B = dict(zip(A_cross, B_cross)), dict(zip(B_cross, A_cross))
	new_A, new_B = [], []
	for i in range(r1):
		a, b = A[i], B[i]
		while a in A2B:
			a = A2B[a]
		while b in B2A:
			b = B2A[b]
		new_A.append(a)
		new_B.append(b)
	new_A += B_cross
	new_B += A_cross
	for i in range(r2+1, l):
		a, b = A[i], B[i]
		while a in A2B:
			a = A2B[a]
		while b in B2A:
			b = B2A[b]
		new_A.append(a)
		new_B.append(b)
	return new_A, new_B

def mutate(A):
	l = len(A)
	r1, r2 = random.randint(0, l-1), random.randint(0, l-1)
	new_A = A
	new_A[r1], new_A[r2] = new_A[r2], new_A[r1]
	return new_A

# 生成新种群
solution_groups = []
for _ in range(pop):
	new_solution = list(range(cargo_count))
	random.shuffle(new_solution)
	solution_groups.append(new_solution)

for i in range(iter_max):
	print('\r', end = "")
	print('第%d次迭代'%(i), end = "")
	sys.stdout.flush()
	tmp = []
	score_map = [(solution, placement(cargos, solution, box_size)[1]) for solution in solution_groups]
	total_score = sum([math.exp(score) for _, score in score_map])
	# 选择
	for _ in range(pop):
		selected_score = random.uniform(0, total_score)
		current_score = 0
		for solution, score in score_map:
			current_score += math.exp(score)
			if current_score + 1e8 >= selected_score:
				tmp.append(solution)
				break
	# 交叉
	for i in range(pop-1):
		tmp[i], tmp[i+1] = pm_crossover(tmp[i], tmp[i+1])
	tmp[pop-1], tmp[0] = pm_crossover(tmp[pop-1], tmp[0])
	# 变异
	for i in range(pop):
		tmp[i] = mutate(tmp[i])

	solution_groups = tmp

score_map = [(solution, placement(cargos, solution, box_size)[1]) for solution in solution_groups]
solution, score = max(score_map, key = lambda x:x[1])

# 退火算法
print('\n\n退火算法......')
T = T_begin
while T > T_end:
	print('\r', end = "")
	print('温度:%.2f    当前分数:%.2f'%(T, score), end = "")
	sys.stdout.flush()
	for _ in range(repeat):
		new_solution = mutate(solution)
		new_answer, new_score = placement(cargos, solution, box_size)
		if new_score > score:
			solution, answer, score = new_solution, new_answer, new_score
		elif random.random() < math.exp((new_score - score) * 100 * T_begin / T):
			solution, answer, score = new_solution, new_answer, new_score
	T = T * cool

print('\n', answer, score)