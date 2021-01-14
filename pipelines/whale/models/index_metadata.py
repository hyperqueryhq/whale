from typing import Dict, Iterable, List, Optional, Union

from whale.models.table_metadata import ColumnMetadata


class IndexMetadata:
    """
    Metadata on indexes
    """

    INDEX_TEMPLATE = "* {type_list} `{name}` [{column_list}]"

    def __init__(
        self,
        database: str,
        cluster: str,
        schema: str,
        table: str,
        name: str,
        columns: Iterable[str],
        description: Optional[str] = None,
        index_type: Optional[str] = None,
        architecture: Optional[str] = None,
        constraint: Optional[str] = None,
        tags: Optional[Union[List[Dict], List[str]]] = None,
    ):
        # type: (...) -> None
        """
        :param database: Name of the database
        :param cluster: Name of the cluster
        :param schema: Name of the table schema
        :param table: Name of the table
        :param name: Name of the index
        :param columns: List of columns contained in the index
        :param description: Description of the index
        :param index_type: Type of index, e.g. primary / secondary
        :param architecture: Index architecture, e.g. clustered / non-clustered
        :param constraint: Constraint the index imposes, e.g. uniqueness
        :param tags: Tag of index
        """

        self.database = database
        self.name = name
        self.cluster = cluster
        self.schema = schema
        self.table = table
        self.description = description
        self.index_type = index_type
        self.architecture = architecture
        self.constraint = constraint
        self.columns = columns
        self.tags = tags

    def __repr__(self):
        # type: () -> str
        return "IndexMetadata({!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r}, {!r})".format(
            self.database,
            self.cluster,
            self.schema,
            self.table,
            self.name,
            self.description,
            self.index_type,
            self.architecture,
            self.constraint,
            self.columns,
            self.tags,
        )

    def format_for_markdown(self):
        type_list = []

        if self.index_type:
            type_list.append(self.index_type)

        if self.constraint:
            type_list.append(self.constraint)

        if self.architecture:
            type_list.append(self.architecture)

        type_list_concat = "[" + ", ".join(type_list) + "]"
        column_list_concat = ", ".join(
            ["`{column}`".format(column=column) for column in self.columns]
        )

        formatted_index = self.INDEX_TEMPLATE.format(
            type_list=type_list_concat,
            name=self.name,
            column_list=column_list_concat,
        )

        formatted_indexes_list = []
        formatted_indexes_list.append(formatted_index)

        return "\n".join(formatted_indexes_list)
