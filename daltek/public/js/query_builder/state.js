// Estado global y mockDB

const state = {
  table: null,
  selectedCols: [],
  filters: [],
};

const mockDB = {
  users: {
    cols: ["id", "name", "email", "role", "created_at", "active"],
    rows: [
      {
        id: 1,
        name: "Ana Perez",
        email: "ana@example.com",
        role: "admin",
        created_at: "2024-04-01",
        active: true,
      },
      {
        id: 2,
        name: "Luis Gomez",
        email: "luis@example.com",
        role: "editor",
        created_at: "2024-05-15",
        active: true,
      },
      {
        id: 3,
        name: "María Ruiz",
        email: "maria@example.com",
        role: "viewer",
        created_at: "2024-06-20",
        active: false,
      },
      {
        id: 4,
        name: "John Doe",
        email: "john@ex.com",
        role: "editor",
        created_at: "2024-07-01",
        active: true,
      },
    ],
  },
  orders: {
    cols: ["order_id", "user_id", "amount", "status", "created_at"],
    rows: [
      {
        order_id: 101,
        user_id: 1,
        amount: 49.99,
        status: "paid",
        created_at: "2025-01-01",
      },
      {
        order_id: 102,
        user_id: 2,
        amount: 19.5,
        status: "pending",
        created_at: "2025-01-05",
      },
      {
        order_id: 103,
        user_id: 1,
        amount: 7.0,
        status: "refunded",
        created_at: "2025-02-10",
      },
    ],
  },
  products: {
    cols: ["sku", "title", "price", "stock", "category"],
    rows: [
      {
        sku: "A-001",
        title: "Camisa",
        price: 25.0,
        stock: 56,
        category: "Ropa",
      },
      {
        sku: "B-010",
        title: "Mouse",
        price: 19.99,
        stock: 10,
        category: "Electrónica",
      },
    ],
  },
};
