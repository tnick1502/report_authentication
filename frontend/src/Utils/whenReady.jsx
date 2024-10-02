export default function whenReady() {
    return new Promise((resolve) => {
        setTimeout(()=>{
            resolve();
        }, 0)
    })
}