class Payee {
  final String id;
  final String name;
  final String budgetId;
  final String? transferAccountId;
  final bool deleted;

  Payee({
    required this.id,
    required this.name,
    required this.budgetId,
    required this.deleted,
    this.transferAccountId,
  });

  factory Payee.fromJson(Map<String, dynamic> json) {
    return Payee(
      id: json['id'],
      name: json['name'],
      budgetId: json['budget_id'],
      deleted: json['deleted'] ?? false,
      transferAccountId: json['transfer_account_id'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'budget_id': budgetId,
        'deleted': deleted,
        'transfer_account_id': transferAccountId,
      };
}
