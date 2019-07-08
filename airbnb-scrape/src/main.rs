use fantoccini::{Client, Locator};
use futures::future::Future;
use tokio;

fn main() {
    let client = Client::new("http://localhost:4444");

    tokio::run(
        client
            .map_err(|error| {
                unimplemented!("failed to connect to WebDriver: {:?}", error)
            })
            .and_then(|client| {
                client.goto("https://www.airbnb.com/")
            })
            .map_err(|error| {
                panic!("a WebDriver command failed: {:?}", error);
            })
    );
}
