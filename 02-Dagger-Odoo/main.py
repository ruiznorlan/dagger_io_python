import sys
import anyio
import dagger


async def test():
    async with dagger.Connection(dagger.Config(log_output=sys.stderr)) as client:

        # -------------------------------------------------------------------------
        # POSTGRES - ENV
        # -------------------------------------------------------------------------

        postgres_data = "/var/lib/postgresql/data"
        postgres_db = "postgres"
        postgres_user = "odoo"
        postgres_password = "odoo"

        # -------------------------------------------------------------------------
        # ODOO - ENV
        # -------------------------------------------------------------------------

        odoo_database = "o16_demo"
        odoo_modules = "base"

        # -------------------------------------------------------------------------
        # FILES
        # -------------------------------------------------------------------------

        extra_addons = client.host().directory("./extra-addons")
        config = client.host().directory("./config")

        # -------------------------------------------------------------------------
        # postgres - CONTAINER
        # -------------------------------------------------------------------------

        postgres_dev_o16 = (
            client.container()
            .from_("postgres:15-alpine")
            .with_env_variable("POSTGRES_DB", postgres_db)
            .with_env_variable("POSTGRES_USER", postgres_user)
            .with_env_variable("POSTGRES_PASSWORD", postgres_password)
            .with_env_variable("PGDATA", postgres_data)
            .with_exec(["postgres"])
            .with_exposed_port(5432)
        )

        # -------------------------------------------------------------------------
        # ODOO - CONTAINER
        # -------------------------------------------------------------------------

        odoo_dev_o16 = (
            client.container()
            .from_("odoo:16.0")
            .with_service_binding("db", postgres_dev_o16)
            .with_env_variable("DB_HOST", "db")
            .with_env_variable("DB_PASSWORD", postgres_password)
            .with_env_variable("DB_USER", postgres_user)
            .with_env_variable("DB_NAME", postgres_db)
            .with_mounted_directory("/mnt/extra-addons", extra_addons)
            .with_mounted_directory("/etc/odoo", config)
            .with_workdir("/")
            .with_exec(["pip3", "install", "websocket-client"])
            .with_exec(
                [
                    "odoo",
                    "-d", odoo_database,
                    "-i", odoo_modules,
                    "--log-handler=:TEST",
                    "--test-enable",
                    "--stop-after-init"
                ]
            )
        )

        # execute
        results = await odoo_dev_o16.stdout()

    print(results)


if __name__ == "__main__":
    anyio.run(test)
