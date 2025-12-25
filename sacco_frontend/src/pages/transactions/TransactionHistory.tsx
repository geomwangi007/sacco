
import React, { useState, useEffect } from "react";
import {
    Box,
    Typography,
    Paper,
    Chip,
    IconButton,
    Grid,
    TextField,
    MenuItem,
    InputAdornment,
    CircularProgress
} from "@mui/material";
import {
    FilterList,
    Refresh,
    Description
} from "@mui/icons-material";
import { DataGrid, GridColDef, GridRenderCellParams } from "@mui/x-data-grid";
import { transactionsApi } from "@/api/transactions.api";
import { Transaction } from "@/types/transaction.types";

const TransactionHistory: React.FC = () => {
    const [transactions, setTransactions] = useState<Transaction[]>([]);
    const [loading, setLoading] = useState(true);
    const [totalCount, setTotalCount] = useState(0);
    const [page, setPage] = useState(0);
    const [pageSize, setPageSize] = useState(10);
    const [statusFilter, setStatusFilter] = useState<string>("all");
    const [typeFilter, setTypeFilter] = useState<string>("all");

    const fetchTransactions = async () => {
        setLoading(true);
        try {
            const data = await transactionsApi.getTransactions({
                page: page + 1,
                status: statusFilter === "all" ? undefined : statusFilter,
                transaction_type: typeFilter === "all" ? undefined : typeFilter
            });
            setTransactions(data.results);
            setTotalCount(data.count);
        } catch (error) {
            console.error("Error fetching transactions:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTransactions();
    }, [page, pageSize, statusFilter, typeFilter]);

    const handleRefresh = () => {
        fetchTransactions();
    };

    const columns: GridColDef[] = [
        { field: 'transaction_ref', headerName: 'Reference', width: 140 },
        { field: 'transaction_type', headerName: 'Type', width: 150 },
        {
            field: 'amount', headerName: 'Amount', width: 140, valueFormatter: (params) => {
                if (params.value == null) return '';
                return `Ugx ${params.value.toLocaleString()}`;
            }
        },
        { field: 'payment_method', headerName: 'Method', width: 130 },
        {
            field: 'status',
            headerName: 'Status',
            width: 120,
            renderCell: (params: GridRenderCellParams) => {
                const status = params.value as string;
                let color = "default";
                if (status === "COMPLETED") color = "success";
                else if (status === "PENDING") color = "warning";
                else if (status === "FAILED") color = "error";
                // eslint-disable-next-line @typescript-eslint/no-explicit-any
                return <Chip label={status} color={color as any} size="small" />;
            }
        },
        {
            field: 'created_at',
            headerName: 'Date',
            width: 160,
            valueGetter: (params) => new Date(params.row.created_at).toLocaleString()
        },
        {
            field: 'actions',
            headerName: 'Actions',
            width: 80,
            sortable: false,
            renderCell: (params) => (
                <IconButton onClick={() => console.log("View Receipt", params.row.id)}>
                    <Description />
                </IconButton>
            )
        }
    ];

    return (
        <Box>
            <Grid container spacing={3} alignItems="center" sx={{ mb: 3 }}>
                <Grid item xs={12} md={6}>
                    <Typography variant="h5" fontWeight={700} color="primary.main">
                        Transaction History
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                        View financial record of all transactions
                    </Typography>
                </Grid>
            </Grid>

            {/* Filters */}
            <Paper sx={{ mb: 3, p: 2 }}>
                <Grid container spacing={2} alignItems="center">
                    <Grid item xs={12} sm={3}>
                        <TextField
                            select
                            fullWidth
                            label="Filter by Type"
                            value={typeFilter}
                            onChange={(e) => setTypeFilter(e.target.value)}
                            size="small"
                        >
                            <MenuItem value="all">All Types</MenuItem>
                            <MenuItem value="DEPOSIT">Deposit</MenuItem>
                            <MenuItem value="WITHDRAWAL">Withdrawal</MenuItem>
                            <MenuItem value="LOAN_DISBURSEMENT">Loan Disbursement</MenuItem>
                            <MenuItem value="LOAN_REPAYMENT">Loan Repayment</MenuItem>
                        </TextField>
                    </Grid>
                    <Grid item xs={12} sm={3}>
                        <TextField
                            select
                            fullWidth
                            label="Filter by Status"
                            value={statusFilter}
                            onChange={(e) => setStatusFilter(e.target.value)}
                            size="small"
                        >
                            <MenuItem value="all">All Statuses</MenuItem>
                            <MenuItem value="COMPLETED">Completed</MenuItem>
                            <MenuItem value="PENDING">Pending</MenuItem>
                            <MenuItem value="FAILED">Failed</MenuItem>
                        </TextField>
                    </Grid>
                    <Grid item xs={12} sm={6} display="flex" justifyContent="flex-end">
                        <IconButton onClick={handleRefresh} color="primary">
                            <Refresh />
                        </IconButton>
                    </Grid>
                </Grid>
            </Paper>

            <Paper sx={{ width: '100%', height: 600 }}>
                <DataGrid
                    rows={transactions}
                    columns={columns}
                    rowCount={totalCount}
                    loading={loading}
                    paginationMode="server"
                    paginationModel={{ page, pageSize }}
                    onPaginationModelChange={(newModel) => {
                        setPage(newModel.page);
                        setPageSize(newModel.pageSize);
                    }}
                    pageSizeOptions={[10, 25, 50]}
                    disableRowSelectionOnClick
                />
            </Paper>
        </Box>
    );
};

export default TransactionHistory;
