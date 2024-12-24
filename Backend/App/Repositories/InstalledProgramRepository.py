from typing import List, Optional

from Backend.App.Models.ProgramModel import ProgramModel


class InstalledProgramRepository:
    """Repository class for managing ProgramModel interactions with the database."""

    @staticmethod
    def add_program(program: ProgramModel) -> None:
        """Add a new Program to the database."""
        program.save()

    @staticmethod
    def get_program_by_client_id(client_uuid: str) -> List[ProgramModel]:
        """Retrieve a program by client id."""
        print(client_uuid)

        return ProgramModel.get(client_uuid=client_uuid)