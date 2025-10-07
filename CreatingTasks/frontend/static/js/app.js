class TaskManager {
    constructor() {
        this.socket = null;
        this.currentTaskList = null;
        this.currentTaskListName = '';
        this.isAuthenticated = false;
        this.init();
    }

    init() {
        this.bindEvents();
        this.checkAuthentication();
        this.showSection('task-lists-section');
    }

    bindEvents() {
        // Навигация
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => this.handleNavigation(e));
        });

        // Кнопки создания
        document.getElementById('create-task-list-btn')?.addEventListener('click',
            () => this.showCreateTaskListForm());
        document.getElementById('create-task-btn')?.addEventListener('click',
            () => this.showCreateTaskForm());

        // Формы
        document.getElementById('task-list-form')?.addEventListener('submit',
            (e) => this.createTaskList(e));
        document.getElementById('task-form')?.addEventListener('submit',
            (e) => this.createTask(e));

        // Авторизация
        document.getElementById('login-btn')?.addEventListener('click',
            () => this.showLoginForm());
        document.getElementById('logout-btn')?.addEventListener('click',
            () => this.logout());
    }

    async checkAuthentication() {
        // Проверяем авторизацию (заглушка)
        this.isAuthenticated = false; // Временно false для демо
        this.updateAuthUI();

        if (this.isAuthenticated) {
            await this.loadTaskLists();
        }
    }

    updateAuthUI() {
        const loginBtn = document.getElementById('login-btn');
        const logoutBtn = document.getElementById('logout-btn');
        const usernameSpan = document.getElementById('username');

        if (this.isAuthenticated) {
            loginBtn.style.display = 'none';
            logoutBtn.style.display = 'inline-block';
            usernameSpan.textContent = 'Пользователь';
        } else {
            loginBtn.style.display = 'inline-block';
            logoutBtn.style.display = 'none';
            usernameSpan.textContent = 'Гость';
        }
    }

    handleNavigation(e) {
        const targetSection = e.target.dataset.section;

        // Обновляем активную кнопку навигации
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        e.target.classList.add('active');

        this.showSection(targetSection);
    }

    showSection(sectionId) {
        // Скрываем все секции
        document.querySelectorAll('.content-section').forEach(section => {
            section.classList.add('hidden');
        });

        // Показываем выбранную секцию
        const targetSection = document.getElementById(sectionId);
        if (targetSection) {
            targetSection.classList.remove('hidden');
        }

        // Загружаем данные для секции
        if (sectionId === 'task-lists-section' && this.isAuthenticated) {
            this.loadTaskLists();
        } else if (sectionId === 'notifications-section' && this.isAuthenticated) {
            this.loadNotifications();
        }
    }

    async loadTaskLists() {
        if (!this.isAuthenticated) {
            this.showLoginPrompt();
            return;
        }

        try {
            // Заглушка для демонстрации
            const mockTaskLists = [
                {
                    id: 1,
                    name: 'Рабочие задачи',
                    description: 'Задачи по работе',
                    tasks_count: 3,
                    members_count: 2
                },
                {
                    id: 2,
                    name: 'Личные задачи',
                    description: 'Личные дела',
                    tasks_count: 1,
                    members_count: 1
                }
            ];

            this.renderTaskLists(mockTaskLists);
        } catch (error) {
            console.error('Ошибка загрузки списков задач:', error);
            this.showError('Не удалось загрузить списки задач');
        }
    }

    renderTaskLists(taskLists) {
        const container = document.getElementById('task-lists-container');
        if (!container) return;

        if (taskLists.length === 0) {
            container.innerHTML = '<p class="empty-state">У вас пока нет списков задач</p>';
            return;
        }

        container.innerHTML = taskLists.map(list => `
            <div class="task-list-card" data-list-id="${list.id}">
                <h3>${list.name}</h3>
                <p class="task-list-description">${list.description || ''}</p>
                <div class="task-list-meta">
                    <span>📋 Задач: ${list.tasks_count || 0}</span>
                    <span>👥 Участников: ${list.members_count || 1}</span>
                </div>
                <div class="task-actions">
                    <button class="btn btn-primary" onclick="taskManager.selectTaskList(${list.id}, '${list.name}')">
                        Открыть
                    </button>
                </div>
            </div>
        `).join('');
    }

    selectTaskList(listId, listName) {
        this.currentTaskList = listId;
        this.currentTaskListName = listName;

        // Обновляем заголовок
        document.getElementById('current-list-name').textContent = `📋 Задачи: ${listName}`;

        // Показываем секцию задач
        this.showSection('tasks-section');

        // Загружаем задачи
        this.loadTasks(listId);
    }

    async loadTasks(listId) {
        if (!this.isAuthenticated) {
            this.showLoginPrompt();
            return;
        }

        try {
            // Заглушка для демонстрации
            const mockTasks = [
                {
                    id: 1,
                    title: 'Завершить проект',
                    description: 'Завершить работу над CreatingTasks',
                    status: 'in_progress',
                    priority: 'high',
                    due_date: '2025-10-10T18:00:00',
                    assigned_to: { username: 'Вы' },
                    is_overdue: false
                },
                {
                    id: 2,
                    title: 'Написать документацию',
                    description: 'Создать документацию для API',
                    status: 'pending',
                    priority: 'medium',
                    due_date: '2025-10-08T12:00:00',
                    assigned_to: { username: 'Вы' },
                    is_overdue: true
                }
            ];

            this.renderTasks(mockTasks);
        } catch (error) {
            console.error('Ошибка загрузки задач:', error);
            this.showError('Не удалось загрузить задачи');
        }
    }

    renderTasks(tasks) {
        const container = document.getElementById('tasks-container');
        if (!container) return;

        if (tasks.length === 0) {
            container.innerHTML = '<p class="empty-state">В этом списке пока нет задач</p>';
            return;
        }

        container.innerHTML = tasks.map(task => this.createTaskHTML(task)).join('');
    }

    createTaskHTML(task) {
        const dueDate = task.due_date ? new Date(task.due_date).toLocaleDateString('ru-RU') : 'Не установлен';
        const isOverdue = task.is_overdue ? 'overdue' : '';

        return `
            <div class="task-card ${isOverdue}" data-task-id="${task.id}">
                <div class="task-header">
                    <h4>${task.title}</h4>
                    <span class="task-priority ${task.priority}">${this.getPriorityText(task.priority)}</span>
                </div>
                <p class="task-description">${task.description || ''}</p>
                <div class="task-meta">
                    <span>👤 Исполнитель: ${task.assigned_to?.username || 'Не назначен'}</span>
                    <span>📅 Срок: ${dueDate}</span>
                    <span>📊 Статус: ${this.getStatusText(task.status)}</span>
                </div>
                <div class="task-actions">
                    ${task.status !== 'completed' ?
                        `<button class="btn btn-success" onclick="taskManager.completeTask(${task.id})">
                            ✅ Завершить
                        </button>` : ''
                    }
                    <button class="btn btn-secondary" onclick="taskManager.showTaskDetails(${task.id})">
                        📋 Подробности
                    </button>
                </div>
            </div>
        `;
    }

    getPriorityText(priority) {
        const priorities = {
            'low': '🔵 Низкий',
            'medium': '🟡 Средний',
            'high': '🟠 Высокий',
            'urgent': '🔴 Срочный'
        };
        return priorities[priority] || priority;
    }

    getStatusText(status) {
        const statuses = {
            'pending': '⏳ Ожидает',
            'in_progress': '🔄 В работе',
            'completed': '✅ Завершена',
            'cancelled': '❌ Отменена'
        };
        return statuses[status] || status;
    }

    showCreateTaskListForm() {
        if (!this.isAuthenticated) {
            this.showLoginPrompt();
            return;
        }
        this.showModal('create-task-list-modal');
    }

    showCreateTaskForm() {
        if (!this.isAuthenticated) {
            this.showLoginPrompt();
            return;
        }
        this.showModal('create-task-modal');
    }

    async createTaskList(e) {
        e.preventDefault();
        const formData = new FormData(e.target);

        // Заглушка для демонстрации
        console.log('Создание списка задач:', {
            name: formData.get('name'),
            description: formData.get('description')
        });

        this.hideModal('create-task-list-modal');
        e.target.reset();
        this.showSuccess('Список задач создан!');

        // Перезагружаем списки
        await this.loadTaskLists();
    }

    async createTask(e) {
        e.preventDefault();
        const formData = new FormData(e.target);

        // Заглушка для демонстрации
        console.log('Создание задачи:', {
            title: formData.get('title'),
            description: formData.get('description'),
            priority: formData.get('priority'),
            due_date: formData.get('due_date')
        });

        this.hideModal('create-task-modal');
        e.target.reset();
        this.showSuccess('Задача создана!');

        // Перезагружаем задачи
        if (this.currentTaskList) {
            await this.loadTasks(this.currentTaskList);
        }
    }

    async completeTask(taskId) {
        if (!this.isAuthenticated) {
            this.showLoginPrompt();
            return;
        }

        // Заглушка для демонстрации
        console.log('Завершение задачи:', taskId);
        this.showSuccess('Задача завершена!');

        // Перезагружаем задачи
        if (this.currentTaskList) {
            await this.loadTasks(this.currentTaskList);
        }
    }

    showTaskDetails(taskId) {
        // Заглушка для демонстрации
        alert(`Детали задачи #${taskId}\n\nЭто демонстрационная версия. В реальном приложении здесь будет подробная информация о задаче.`);
    }

    showLoginForm() {
        // Заглушка для демонстрации
        alert('Форма входа\n\nЭто демонстрационная версия. В реальном приложении здесь будет форма входа.');
    }

    logout() {
        this.isAuthenticated = false;
        this.updateAuthUI();
        this.showSection('task-lists-section');
        this.showSuccess('Вы вышли из системы');
    }

    showModal(modalId) {
        document.getElementById(modalId)?.classList.remove('hidden');
    }

    hideModal(modalId) {
        document.getElementById(modalId)?.classList.add('hidden');
    }

    showLoginPrompt() {
        this.showError('Для выполнения этого действия необходимо войти в систему');
    }

    showError(message) {
        this.showNotification(message, 'error');
    }

    showSuccess(message) {
        this.showNotification(message, 'success');
    }

    showNotification(message, type = 'info') {
        // Создаем временное уведомление
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <p>${message}</p>
            </div>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'error' ? '#f8d7da' : type === 'success' ? '#d1edff' : '#fff3cd'};
            border: 1px solid ${type === 'error' ? '#f5c6cb' : type === 'success' ? '#b8daff' : '#ffeaa7'};
            color: ${type === 'error' ? '#721c24' : type === 'success' ? '#155724' : '#856404'};
            padding: 1rem;
            border-radius: 5px;
            z-index: 10000;
            max-width: 300px;
        `;

        document.body.appendChild(notification);

        // Автоматически удаляем через 5 секунд
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 5000);
    }

    loadNotifications() {
        // Заглушка для демонстрации
        const mockNotifications = [
            {
                id: 1,
                title: 'Новая задача',
                message: 'Вам назначена новая задача "Завершить проект"',
                is_read: false,
                created_at: new Date().toISOString()
            },
            {
                id: 2,
                title: 'Срок истекает',
                message: 'Задача "Написать документацию" просрочена',
                is_read: true,
                created_at: new Date(Date.now() - 3600000).toISOString()
            }
        ];

        this.renderNotifications(mockNotifications);
    }

    renderNotifications(notifications) {
        const container = document.getElementById('notifications-container');
        if (!container) return;

        if (notifications.length === 0) {
            container.innerHTML = '<p class="empty-state">У вас нет уведомлений</p>';
            return;
        }

        container.innerHTML = notifications.map(notification => `
            <div class="notification ${notification.is_read ? '' : 'unread'}">
                <div class="notification-content">
                    <h4>${notification.title}</h4>
                    <p>${notification.message}</p>
                    <div class="notification-time">
                        ${new Date(notification.created_at).toLocaleString('ru-RU')}
                    </div>
                </div>
            </div>
        `).join('');
    }
}

// Инициализация приложения
const taskManager = new TaskManager();