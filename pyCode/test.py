def greedy_coin_change(coin_values, amount):
    """
    使用贪心算法解决硬币找零问题。
    参数:
    coin_values: 可用的硬币面额列表。
    amount: 需要找零的总金额。
    返回:
    使用的硬币的数量和每种硬币的使用数量。
    """
    # 将硬币面额按照从大到小的顺序排序
    coin_values.sort(reverse=True)
    # 初始化结果字典，记录每种面额硬币的使用数量
    coin_count = {}
    # 初始化总使用硬币的数量
    total_coins = 0

    # 遍历每种硬币
    for coin in coin_values:
        # 计算当前硬币能使用的最大数量
        count = amount // coin
        if count > 0:
            coin_count[coin] = count  # 记录使用数量
            amount -= coin * count    # 更新剩余需要找零的金额
            total_coins += count      # 更新总硬币数量

        # 如果金额已经找零完毕，终止循环
        if amount == 0:
            break

    # 如果还有剩余金额未找零完毕，说明找零失败
    if amount > 0:
        return "找零失败：剩余金额无法用给定硬币组合。"
    else:
        return total_coins, coin_count

# 示例
coin_values = [25, 10, 5, 1]
amount = 63
print("使用的硬币数量和每种硬币的使用详情:", greedy_coin_change(coin_values, amount))
