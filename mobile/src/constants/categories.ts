export const EXPENSE_CATEGORIES = [
  { id: 'Food', label: '🍔 Food', color: '#ef4444' },
  { id: 'Transport', label: '🚗 Transport', color: '#f97316' },
  { id: 'Housing', label: '🏠 Housing', color: '#eab308' },
  { id: 'Bills', label: '💡 Bills', color: '#22c55e' },
  { id: 'Entertainment', label: '🎉 Fun', color: '#3b82f6' },
  { id: 'Shopping', label: '🛍️ Shopping', color: '#8b5cf6' },
  { id: 'Health', label: '🏥 Health', color: '#ec4899' },
  { id: 'Other', label: '📦 Other', color: '#6b7280' },
];

export const INCOME_CATEGORIES = [
  { id: 'Salary', label: '💰 Salary', color: '#22c55e' },
  { id: 'Freelance', label: '💻 Freelance', color: '#3b82f6' },
  { id: 'Investment', label: '📈 Investment', color: '#8b5cf6' },
  { id: 'Gift', label: '🎁 Gift', color: '#ec4899' },
  { id: 'Other', label: '📦 Other', color: '#6b7280' },
];

export const INCOME_CATEGORY_IDS = INCOME_CATEGORIES.map(c => c.id);
export const EXPENSE_CATEGORY_IDS = EXPENSE_CATEGORIES.map(c => c.id);
