
export class Room {
    constructor(
      public id: BigInteger,
      public name: string,
      public roomStatus: string,
      public masterToken: string
    ) {}
  
    isUserMaster(userToken: string): boolean {
      return this.masterToken === userToken;
    }
  }
  