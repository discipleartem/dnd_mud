class ProjectStructureValidator:
    """Валидатор структуры проекта."""
    
    @staticmethod
    def validate_data_directory(data_dir: Path) -> None:
        """Проверяет наличие необходимых директорий."""
        if not data_dir.exists():
            raise FileNotFoundError(f"Директория данных не найдена: {data_dir}")

        required_subdirs = ["yaml", "saves", "mods", "adventures"]
        for subdir in required_subdirs:
            if not (data_dir / subdir).exists():
                (data_dir / subdir).mkdir(parents=True, exist_ok=True)