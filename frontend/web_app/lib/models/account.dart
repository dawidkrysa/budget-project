class Account {
  final String id;
  final String name;
  final String budgetId;
  final String balance;
  final String? transferPayeeId;
  final String typeId;
  final bool deleted;

  Account({
    required this.id,
    required this.name,
    required this.budgetId,
    required this.balance,
    required this.typeId,
    required this.deleted,
    this.transferPayeeId,
  });

  factory Account.fromJson(Map<String, dynamic> json) {
    return Account(
      id: json['id'],
      name: json['name'],
      budgetId: json['budget_id'],
      balance: json['balance'],
      typeId: json['type_id'],
      deleted: json['deleted'] ?? false,
      transferPayeeId: json['transfer_payee_id'],
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'budget_id': budgetId,
        'balance': balance,
        'type_id': typeId,
        'deleted': deleted,
        'transfer_payee_id': transferPayeeId,
      };
}
