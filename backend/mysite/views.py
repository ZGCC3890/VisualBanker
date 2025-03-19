import random
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def banker_algorithm(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        n = data.get("n", 5)  # 客户数
        m = data.get("m", 3)  # 资源种类数
        
        # --------------------------
        # 1. 生成每个客户的最大需求 Max 和资源占用时间
        # --------------------------
        max_resources = [
            [random.randint(1, 10) for _ in range(m)] 
            for _ in range(n)
        ]
        # 随机生成每个客户的“资源占用时间”
        execute_time = [
            random.randint(1, 10) 
            for _ in range(n)
        ]

        # --------------------------
        # 2. 根据 max_resources 来决定总资源量 total_resources
        # --------------------------
        sum_demand_per_resource = [0] * m
        for i in range(n):
            for j in range(m):
                sum_demand_per_resource[j] += max_resources[i][j]

        # 总资源在 sum_demand_per_resource 附近上下浮动(0.6 - 1.4)
        total_resources = []
        for j in range(m):
            low = int(0.6 * sum_demand_per_resource[j])
            high = int(1.4 * sum_demand_per_resource[j]) if sum_demand_per_resource[j] > 0 else 1
            # 避免出现 low > high 或总为 0 的情况
            low = max(low, 1)
            high = max(high, low)
            total_resources.append(random.randint(low, high))

        # --------------------------
        # 3. 随机生成已分配矩阵 Allocation，并计算 Available
        # --------------------------
        allocation = [[0]*m for _ in range(n)]
        # 因为要保证分配不超过 total_resources，对每种资源做独立分配
        available = total_resources[:]
        for j in range(m):
            remain = available[j]
            for i in range(n):
                if remain <= 0:
                    break
                # 当前客户 i 能分配的最大资源不超过其最大需求
                max_alloc = min(max_resources[i][j], remain)
                # 在 [0, max_alloc] 区间随机分配
                alloc = random.randint(0, max_alloc)
                allocation[i][j] = alloc
                remain -= alloc
            available[j] = remain

        # 计算 Need 矩阵
        need = [
            [max_resources[i][j] - allocation[i][j] for j in range(m)]
            for i in range(n)
        ]

        # --------------------------
        # 4. 定义单次安全性检查 (找一种安全序列)
        # --------------------------
        def is_safe_once():
            work = available[:]
            finish = [False]*n
            safe_sequence = []
            while len(safe_sequence) < n:
                found = False
                for i in range(n):
                    if not finish[i] and all(need[i][k] <= work[k] for k in range(m)):
                        # 分配资源
                        for k in range(m):
                            work[k] += allocation[i][k]
                        safe_sequence.append(i)
                        finish[i] = True
                        found = True
                        break
                if not found:
                    return False, []
            return True, safe_sequence

        # --------------------------
        # 5. 回溯搜索所有安全序列
        # --------------------------
        def find_all_safe_sequences():
            results = []
            used = [False]*n
            work = available[:]

            def backtrack(seq, work_snapshot):
                # 如果序列长度 == n，找到了一条完整可行序列
                if len(seq) == n:
                    results.append(seq[:])
                    return
                for i in range(n):
                    if (not used[i]) and all(need[i][k] <= work_snapshot[k] for k in range(m)):
                        # “执行”进程 i
                        used[i] = True
                        # 临时保存旧的 work
                        old_work = work_snapshot[:]
                        # “分配”给 i
                        for k in range(m):
                            work_snapshot[k] += allocation[i][k]
                        seq.append(i)

                        # 递归
                        backtrack(seq, work_snapshot)

                        # 回溯
                        seq.pop()
                        used[i] = False
                        work_snapshot = old_work

            backtrack([], work)
            return results

        # --------------------------
        # 6. 计算资源利用率
        # --------------------------
        def calc_resource_utilization(sequence):
            work = available[:]
            max_utilization = 0
            for i in sequence:
                for k in range(m):
                    work[k] -= need[i][k]
                utilization = 1 - (sum(work) / sum(total_resources))
                max_utilization = max(max_utilization, utilization)
                for k in range(m):
                    work[k] += need[i][k]
                    work[k] += allocation[i][k]
            return max_utilization * 100

        # 先检查是否有安全序列
        safe_once, first_seq = is_safe_once()
        all_seqs = []
        best_seq = []
        if safe_once:
            all_seqs = find_all_safe_sequences()
            seq_with_utilization = [(seq, calc_resource_utilization(seq)) for seq in all_seqs]
            seq_with_utilization.sort(key=lambda x: x[1], reverse=True)  # 按资源利用率降序排序
            best_seq = seq_with_utilization[0][0]  # 取资源利用率最高的序列
        else:
            pass

        return JsonResponse({
            "total_resources": total_resources,
            "max_resources": max_resources,
            "allocation": allocation,
            "need": need,
            "available": available,
            "execute_time": execute_time,
            "safe": safe_once,
            "one_safe_sequence": first_seq,
            "all_safe_sequences": all_seqs,
            "best_sequence": best_seq,
            "utilization_per_sequence": [calc_resource_utilization(seq) for seq in all_seqs]
        }, safe=False)
    return JsonResponse({"error": "Invalid request"}, status=400)
