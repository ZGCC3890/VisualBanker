import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def banker_algorithm(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        n = data.get("n", 7)  # 客户数
        m = data.get("m", 4)  # 资源种类数

        # 生成总资源（保证充足的资源）
        total_resources = [random.randint(n * 2, n * 5) for _ in range(m)]

        # 生成最大需求矩阵 Max（确保不超过总资源）
        max_resources = [[random.randint(1, total_resources[j]) for j in range(m)] for i in range(n)]

        # 初始化 Allocation（已分配矩阵）和 Available（可用资源）
        allocation = [[0] * m for _ in range(n)]
        available = total_resources[:]

        # 随机分配 Allocation，确保不会超过 Available
        for j in range(m):  # 遍历每种资源
            remaining = total_resources[j]  # 记录该资源的剩余量
            for i in range(n):
                if remaining == 0:
                    break
                # 确保分配的资源不会超过 max_resources[i][j] 以及当前 Available 资源
                alloc = random.randint(0, min(max_resources[i][j], remaining))
                allocation[i][j] = alloc
                remaining -= alloc  # 更新剩余资源
            available[j] = remaining  # 计算最终的 Available

        # 计算 Need 矩阵
        need = [[max_resources[i][j] - allocation[i][j] for j in range(m)] for i in range(n)]

        # 运行安全性算法
        def is_safe():
            work = available[:]
            finish = [False] * n
            safe_sequence = []
            while len(safe_sequence) < n:
                found = False
                for i in range(n):
                    if not finish[i] and all(need[i][j] <= work[j] for j in range(m)):
                        for j in range(m):
                            work[j] += allocation[i][j]
                        safe_sequence.append(i)
                        finish[i] = True
                        found = True
                        break
                if not found:
                    return False, []
            return True, safe_sequence

        safe, sequence = is_safe()

        return JsonResponse({
            "max_resources": max_resources,
            "allocation": allocation,
            "need": need,
            "available": available,
            "safe": safe,
            "sequence": sequence
        })
    return JsonResponse({"error": "Invalid request"}, status=400)
