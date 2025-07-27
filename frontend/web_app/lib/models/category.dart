class Category {
  final String id;
  final String budgetId;
  final String categoryGroupId;
  final String categoryNameId;
  final String categoryName;
  final String activity;
  final String balance;
  final String budgeted;
  final String monthId;
  final bool deleted;
  final bool hidden;

  Category({
    required this.id,
    required this.budgetId,
    required this.categoryGroupId,
    required this.categoryNameId,
    required this.categoryName,
    required this.activity,
    required this.balance,
    required this.budgeted,
    required this.monthId,
    required this.deleted,
    required this.hidden,
  });

  factory Category.fromJson(Map<String, dynamic> json) {
    return Category(
      id: json['id'],
      budgetId: json['budget_id'],
      categoryGroupId: json['category_group_id'],
      categoryNameId: json['category_name_id'],
      categoryName: json['category_name'],
      activity: json['activity'],
      balance: json['balance'],
      budgeted: json['budgeted'],
      monthId: json['month_id'],
      deleted: json['deleted'] ?? false,
      hidden: json['hidden'] ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'budget_id': budgetId,
        'category_group_id': categoryGroupId,
        'category_name_id': categoryNameId,
        'category_name': categoryName,
        'activity': activity,
        'balance': balance,
        'budgeted': budgeted,
        'month_id': monthId,
        'deleted': deleted,
        'hidden': hidden,
      };
}
