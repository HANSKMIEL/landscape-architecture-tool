"""
Tests for database initialization utilities
"""

from unittest.mock import Mock, patch

import pytest

from src.utils.db_init import initialize_database, populate_sample_data


class TestInitializeDatabase:
    """Test database initialization function"""

    @patch("src.utils.db_init.db")
    @patch("src.utils.db_init.logger")
    def test_initialize_database_success(self, mock_logger, mock_db):
        """Test successful database initialization"""
        mock_db.create_all = Mock()

        initialize_database()

        mock_db.create_all.assert_called_once()
        mock_logger.info.assert_called_with("Database tables created successfully")

    @patch("src.utils.db_init.db")
    @patch("src.utils.db_init.logger")
    def test_initialize_database_error(self, mock_logger, mock_db):
        """Test database initialization with error"""
        mock_db.create_all.side_effect = Exception("Database error")

        with pytest.raises(Exception, match="Database error"):
            initialize_database()

        mock_db.create_all.assert_called_once()
        mock_logger.error.assert_called_with("Error creating database tables: Database error")


class TestPopulateSampleData:
    """Test sample data population function"""

    @patch("src.utils.db_init.Supplier")
    @patch("src.utils.db_init.User")
    @patch("src.utils.db_init.db")
    @patch("src.utils.db_init.logger")
    def test_populate_sample_data_skips_if_data_exists(self, mock_logger, mock_db, mock_user, mock_supplier):
        """Test that sample data is skipped if suppliers already exist"""
        # Mock that suppliers already exist
        mock_query = Mock()
        mock_query.count.return_value = 5
        mock_supplier.query = mock_query

        # Mock that users already exist so user creation is skipped
        mock_user_query = Mock()
        mock_user_query.count.return_value = 3
        mock_user.query = mock_user_query

        populate_sample_data()

        mock_logger.info.assert_called_with("Sample business data already exists, skipping initialization")
        # Should not add new suppliers
        mock_db.session.add.assert_not_called()

    @patch("src.utils.db_init.Supplier")
    @patch("src.utils.db_init.Plant")
    @patch("src.utils.db_init.Product")
    @patch("src.utils.db_init.Client")
    @patch("src.utils.db_init.Project")
    @patch("src.utils.db_init.db")
    @patch("src.utils.db_init.logger")
    def test_populate_sample_data_creates_data(
        self,
        mock_logger,
        mock_db,
        mock_project,
        mock_client,
        mock_product,
        mock_plant,
        mock_supplier,
    ):
        """Test that sample data is created when database is empty"""
        # Mock that no suppliers exist
        mock_supplier_query = Mock()
        mock_supplier_query.count.return_value = 0
        mock_supplier.query = mock_supplier_query

        # Mock supplier instances
        mock_supplier_instances = [Mock(id=1), Mock(id=2), Mock(id=3)]
        mock_supplier.side_effect = mock_supplier_instances

        # Mock client instances
        mock_client_instances = [Mock(id=1), Mock(id=2), Mock(id=3)]
        mock_client.side_effect = mock_client_instances

        # Mock plant and product instances
        mock_plant.return_value = Mock()
        mock_product.return_value = Mock()
        mock_project.return_value = Mock()

        # Mock session methods
        mock_db.session.add = Mock()
        mock_db.session.flush = Mock()
        mock_db.session.commit = Mock()

        populate_sample_data()

        # Should log that data creation started
        mock_logger.info.assert_any_call("Populating database with sample business data...")

        # Should create suppliers, plants, products, clients, and projects
        assert mock_supplier.call_count == 3
        assert mock_plant.call_count == 3
        assert mock_product.call_count == 4
        assert mock_client.call_count == 3
        assert mock_project.call_count == 3

        # Should add all items to session
        assert mock_db.session.add.call_count > 0

        # Should flush and commit
        mock_db.session.flush.assert_called()
        assert mock_db.session.commit.call_count == 2

        # Should log success
        mock_logger.info.assert_any_call("Sample business data created successfully!")

    @patch("src.utils.db_init.Supplier")
    @patch("src.utils.db_init.db")
    @patch("src.utils.db_init.logger")
    def test_populate_sample_data_handles_error(self, mock_logger, mock_db, mock_supplier):
        """Test error handling during sample data creation"""
        # Mock that no suppliers exist
        mock_supplier_query = Mock()
        mock_supplier_query.count.return_value = 0
        mock_supplier.query = mock_supplier_query

        # Mock an error during supplier creation
        mock_supplier.side_effect = Exception("Database error")

        # Mock session methods
        mock_db.session.rollback = Mock()

        with pytest.raises(Exception, match="Database error"):
            populate_sample_data()

        # Should rollback on error
        mock_db.session.rollback.assert_called_once()
        mock_logger.error.assert_called_with("Error populating sample data: Database error")

    def test_populate_sample_data_supplier_data_structure(self, app_context):
        del app_context
        """Test that supplier data has expected structure"""
        # Authentication handled by authenticated_test_user fixture
        # This tests the actual data structure without mocking
        with patch("src.utils.db_init.db.session") as mock_session:
            mock_session.add = Mock()
            mock_session.flush = Mock()
            mock_session.commit = Mock()

            with patch("src.utils.db_init.Supplier") as mock_supplier:
                # Set up query mock on the Supplier class
                mock_query = Mock()
                mock_query.count.return_value = 0
                mock_supplier.query = mock_query

                mock_supplier_instances = [Mock(id=1), Mock(id=2), Mock(id=3)]
                created_suppliers = []

                def capture_supplier(*args, **kwargs):
                    supplier = Mock()
                    supplier.configure_mock(**kwargs)
                    created_suppliers.append(kwargs)
                    return mock_supplier_instances[len(created_suppliers) - 1]

                mock_supplier.side_effect = capture_supplier

                # Mock other model classes
                with (
                    patch("src.utils.db_init.Plant"),
                    patch("src.utils.db_init.Product"),
                    patch("src.utils.db_init.Client"),
                    patch("src.utils.db_init.Project"),
                ):
                    populate_sample_data()

                    # Verify supplier data structure
                    assert len(created_suppliers) == 3

                    # Check first supplier
                    first_supplier = created_suppliers[0]
                    assert first_supplier["name"] == "Boomkwekerij Peters"
                    assert first_supplier["contact_person"] == "Jan Peters"
                    assert first_supplier["email"] == "jan@boomkwekerijpeters.nl"
                    assert first_supplier["city"] == "Boskoop"
                    assert first_supplier["specialization"] == "Bomen en heesters"

    def test_populate_sample_data_plant_data_structure(self, app_context):
        del app_context
        """Test that plant data has expected structure"""
        # Authentication handled by authenticated_test_user fixture
        with patch("src.utils.db_init.db.session") as mock_session:
            mock_session.add = Mock()
            mock_session.flush = Mock()
            mock_session.commit = Mock()

            with patch("src.utils.db_init.Supplier") as mock_supplier:
                # Set up query mock on the Supplier class
                mock_query = Mock()
                mock_query.count.return_value = 0
                mock_supplier.query = mock_query

                # Mock supplier instances with IDs
                mock_supplier_instances = [Mock(id=1), Mock(id=2), Mock(id=3)]
                mock_supplier.side_effect = mock_supplier_instances

                with patch("src.utils.db_init.Plant") as mock_plant:
                    created_plants = []

                    def capture_plant(*args, **kwargs):
                        plant = Mock()
                        plant.configure_mock(**kwargs)
                        created_plants.append(kwargs)
                        return Mock()

                    mock_plant.side_effect = capture_plant

                    # Mock other model classes
                    with (
                        patch("src.utils.db_init.Product"),
                        patch("src.utils.db_init.Client"),
                        patch("src.utils.db_init.Project"),
                    ):
                        populate_sample_data()

                        # Verify plant data structure
                        assert len(created_plants) == 3

                        # Check first plant (Acer platanoides)
                        first_plant = created_plants[0]
                        assert first_plant["name"] == "Acer platanoides"
                        assert first_plant["common_name"] == "Noorse esdoorn"
                        assert first_plant["category"] == "Boom"
                        assert first_plant["height_min"] == 15.0
                        assert first_plant["height_max"] == 25.0
                        assert first_plant["sun_requirements"] == "Zon tot halfschaduw"
                        assert first_plant["native"] is True
                        assert first_plant["supplier_id"] == 1  # First supplier's ID

    def test_populate_sample_data_project_data_structure(self, app_context):
        del app_context
        """Test that project data has expected structure"""
        # Authentication handled by authenticated_test_user fixture
        with patch("src.utils.db_init.db.session") as mock_session:
            mock_session.add = Mock()
            mock_session.flush = Mock()
            mock_session.commit = Mock()

            with patch("src.utils.db_init.Supplier") as mock_supplier:
                # Set up query mock on the Supplier class
                mock_query = Mock()
                mock_query.count.return_value = 0
                mock_supplier.query = mock_query

                mock_supplier_instances = [Mock(id=1), Mock(id=2), Mock(id=3)]
                mock_supplier.side_effect = mock_supplier_instances

                with patch("src.utils.db_init.Client") as mock_client:
                    mock_client_instances = [Mock(id=1), Mock(id=2), Mock(id=3)]
                    mock_client.side_effect = mock_client_instances

                    with patch("src.utils.db_init.Project") as mock_project:
                        created_projects = []

                        def capture_project(*args, **kwargs):
                            project = Mock()
                            project.configure_mock(**kwargs)
                            created_projects.append(kwargs)
                            return Mock()

                        mock_project.side_effect = capture_project

                        # Mock other model classes
                        with (
                            patch("src.utils.db_init.Plant"),
                            patch("src.utils.db_init.Product"),
                        ):
                            populate_sample_data()

                            # Verify project data structure
                            assert len(created_projects) == 3

                            # Check first project
                            first_project = created_projects[0]
                            assert first_project["name"] == "Vondelpark Renovatie Fase 2"
                            assert first_project["client_id"] == 2  # Second client (Vondelpark Beheer)
                            assert first_project["status"] == "In uitvoering"
                            assert first_project["budget"] == 75000.00
                            assert first_project["project_manager"] == "Hans Kmiel"

    @patch("src.utils.db_init.logger")
    def test_populate_sample_data_logging(self, mock_logger, app_context):
        del app_context
        """Test that appropriate logging messages are generated"""
        with patch("src.utils.db_init.Supplier.query") as mock_query:
            mock_query.count.return_value = 5  # Data exists

            populate_sample_data()

        mock_logger.info.assert_called_with("Sample business data already exists, skipping initialization")
