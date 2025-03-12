module AptExchange {
    use std::signer;
    use aptos_framework::coin;
    use aptos_framework::account;
    use aptos_framework::aptos_coin;

    struct LiquidityPool has key {
        apt_balance: u64,
        token_balance: u64,
    }
    
    public entry fun initialize_pool(
        account: &signer,
        initial_apt: u64,
        initial_token: u64
    ) {
        let pool = LiquidityPool {
            apt_balance: initial_apt,
            token_balance: initial_token,
        };
        move_to(account, pool);
    }
    
    public entry fun swap_apt_for_token(
        account: &signer,
        amount_in: u64
    ) acquires LiquidityPool {
        let pool = borrow_global_mut<LiquidityPool>(signer::address_of(account));
        let token_out = (amount_in * pool.token_balance) / (pool.apt_balance + amount_in);
        
        // Update pool balances
        pool.apt_balance += amount_in;
        pool.token_balance -= token_out;
        
        coin::transfer(account, signer::address_of(account), token_out);
    }
}